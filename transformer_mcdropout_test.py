import os
import random
import logging
# import basic python packages
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.metrics import f1_score, precision_score, recall_score

# import torch packages
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from deepec.process_data import read_EC_Fasta
from deepec.data_loader import ECDataset, ECEmbedDataset, ECShortEmbedDataset
from deepec.utils import argument_parser, draw, save_losses, FocalLoss, DeepECConfig
from deepec.train import train, evalulate_mcdropout
from deepec.model import DeepTransformer, DeepTransformer_linear

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')


if __name__ == '__main__':
    parser = argument_parser()
    options = parser.parse_args()

    output_dir = options.output_dir
    log_dir = options.log_dir

    device = options.gpu
    num_epochs = options.epoch
    batch_size = options.batch_size
    learning_rate = options.learning_rate
    patience = options.patience

    checkpt_file = options.checkpoint
    input_data_file = options.seq_file

    third_level = options.third_level
    num_cpu = options.cpu_num

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f'{output_dir}/{log_dir}')
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    seed_num = 123 # random seed for reproducibility
    torch.manual_seed(seed_num)
    random.seed(seed_num)
    torch.cuda.manual_seed_all(seed_num)
    np.random.seed(seed_num)

    torch.set_num_threads(num_cpu)

    gamma = 0

    logging.info(f'\nInitial Setting\
                  \nEpoch: {num_epochs}\
                  \tGamma: {gamma}\
                  \tBatch size: {batch_size}\
                  \tLearning rate: {learning_rate}\
                  \tGPU: {device}\
                  \tPredict upto 3 level: {third_level}')
    logging.info(f'Input file directory: {input_data_file}')


    input_seqs, input_ecs, input_ids = read_EC_Fasta(input_data_file)

    _, test_seqs = train_test_split(input_seqs, test_size=0.1, random_state=seed_num)
    _, test_ecs = train_test_split(input_ecs, test_size=0.1, random_state=seed_num)
    # train_ids, test_ids = train_test_split(input_ids, test_size=0.1, random_state=seed_num)

    logging.info(f'Number of sequences used- Test: {len(test_seqs)}')

    explainECs = []
    for ecs in input_ecs:
        explainECs += ecs
    explainECs = list(set(explainECs))
    explainECs.sort()


    test_ec_types = []
    for ecs in test_ecs:
        test_ec_types += ecs
    len_test_ecs = len(set(test_ec_types))

    logging.info(f'Number of ECs in test data: {len_test_ecs}')

    testDataset = ECEmbedDataset(test_seqs, test_ecs, explainECs)
    testDataloader = DataLoader(testDataset, batch_size=batch_size, shuffle=False)

    ntokens = 20
    emsize = 128 # embedding dimension
    nhid = 256 # the dimension of the feedforward network model in nn.TransformerEncoder
    nlayers = 1 # the number of nn.TransformerEncoderLayer in nn.TransformerEncoder
    nhead = 8 # the number of heads in the multiheadattention models
    dropout = 0.2 # the dropout value
    logging.info(f'Network architecture info\n\
                    ntoken {ntokens}\temsize {emsize}\tnhid {nhid}\tnlayers {nlayers}\tnhead {nhead}')
    model = DeepTransformer(ntokens, emsize, nhead, nhid, nlayers, dropout, explainECs)
    # model = DeepTransformer_linear(ntokens, emsize, nhead, nhid, nlayers, dropout, explainECs).to(device)
    model = nn.DataParallel(model, device_ids=[int(device[-1])])
    model = model.to(device)
    # logging.info(f'Model Architecture: \n{model}')
    # num_train_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    # logging.info(f'Number of trainable parameters: {num_train_params}')

    optimizer = optim.Adam(model.parameters(), lr=learning_rate, )
    criterion = FocalLoss(gamma=gamma)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.95)
    # logging.info(f'Learning rate scheduling: step size: 1\tgamma: 0.95')

    config = DeepECConfig()
    config.model = model 
    config.optimizer = optimizer
    config.criterion = criterion
    config.scheduler = scheduler
    config.n_epochs = num_epochs
    config.device = device
    config.save_name = f'{output_dir}/{checkpt_file}'
    config.patience = patience
    config.train_source = None
    config.val_source = None
    config.test_source = testDataloader
    config.explainProts = explainECs

    ckpt = torch.load(f'{output_dir}/{checkpt_file}', map_location=device)
    model.load_state_dict(ckpt['model'])

    y_true, y_score, y_pred, y_pred_std = evalulate_mcdropout(config)
    precision = precision_score(y_true, y_pred, average='macro')
    recall = recall_score(y_true, y_pred, average='macro')
    f1 = f1_score(y_true, y_pred, average='macro')
    logging.info(f'(Macro) Precision: {precision}\tRecall: {recall}\tF1: {f1}')
    
    precision = precision_score(y_true, y_pred, average='micro')
    recall = recall_score(y_true, y_pred, average='micro')
    f1 = f1_score(y_true, y_pred, average='micro')
    logging.info(f'(Micro) Precision: {precision}\tRecall: {recall}\tF1: {f1}')

    logging.info(f'\nMC dropout - one sigma')
    precision = precision_score(y_true, y_pred_std, average='macro')
    recall = recall_score(y_true, y_pred_std, average='macro')
    f1 = f1_score(y_true, y_pred_std, average='macro')
    logging.info(f'(Macro) Precision: {precision}\tRecall: {recall}\tF1: {f1}')
    
    precision = precision_score(y_true, y_pred_std, average='micro')
    recall = recall_score(y_true, y_pred_std, average='micro')
    f1 = f1_score(y_true, y_pred_std, average='micro')
    logging.info(f'(Micro) Precision: {precision}\tRecall: {recall}\tF1: {f1}')
    
    # len_ECs = len(explainECs)

    # fpr = dict()
    # tpr = dict()
    # roc_auc = dict()
    # prec = dict()
    # rec = dict()
    # f1s = dict()

    # for i in range(len_ECs):
    #     fpr[i], tpr[i], _ = roc_curve(y_true[:, i], y_score[:, i])
    #     roc_auc[i] = auc(fpr[i], tpr[i])
    #     prec[i] = precision_score(y_true[:, i], y_pred[:, i], )
    #     rec[i] = recall_score(y_true[:, i], y_pred[:, i])
    #     f1s[i] = f1_score(y_true[:, i], y_pred[:, i])

    # fp = open(f'{output_dir}/performance_indices.txt', 'w')
    # fp.write('EC\tAUC\tPrecision\tRecall\tF1\n')
    # for ind in roc_auc:
    #     ec = explainECs[ind]
    #     fp.write(f'{ec}\t{roc_auc[ind]}\t{prec[ind]}\t{rec[ind]}\t{f1s[ind]}\n')
    # fp.close()