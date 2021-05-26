import re
import torch
import numpy as np
from torch.utils.data import Dataset
from transformers import AutoTokenizer


# create a data loading class for the use of pytorch
# I put the one hot encoding in here
class ECDataset(Dataset):
    def __init__(self, data_X, data_Y, explainECs, pred=False):
        self.pred = pred
        self.data_X = data_X
        self.map_AA = self.getAAmap()

        if not pred:
            self.data_Y = data_Y
            self.map_EC = self.getECmap(explainECs)
        
    
    def __len__(self):
        return len(self.data_X)
    
    
    def getAAmap(self):
        aa_vocab = ['A', 'C', 'D', 'E', 
                    'F', 'G', 'H', 'I', 
                    'K', 'L', 'M', 'N', 
                    'P', 'Q', 'R', 'S',
                    'T', 'V', 'W', 'Y', ]
        map = {}
        for i, char in enumerate(aa_vocab):
            baseArray = np.zeros(len(aa_vocab))
            baseArray[i] = 1
            map[char] = baseArray
        return map
    
    
    def getECmap(self, explainECs):
        ec_vocab = list(set(explainECs))
        ec_vocab.sort()
        map = {}
        for i, ec in enumerate(ec_vocab):
            baseArray = np.zeros(len(ec_vocab))
            baseArray[i] = 1
            map[ec] = baseArray
        return map


    def convert2onehot_seq(self, single_seq, max_seq=1000):
        single_onehot = np.zeros((max_seq, len(self.map_AA)))
        for i, x in enumerate(single_seq):
            single_onehot[i] = np.asarray(self.map_AA[x])
        return single_onehot
    
    
    def convert2onehot_EC(self, EC):
        map_EC = self.map_EC
        single_onehot = np.zeros(len(map_EC))
        for each_EC in EC:
            single_onehot += map_EC[each_EC]
        return single_onehot
    
    
    def __getitem__(self, idx):
        x = self.data_X[idx]
        x = self.convert2onehot_seq(x)
        x = x.reshape((1,) + x.shape)

        if self.pred:
            return x

        y = self.data_Y[idx]
        y = self.convert2onehot_EC(y)
        y = y.reshape(-1)
        return x, y


class ECEmbedDataset(Dataset):
    def __init__(self, data_X, data_Y, explainECs, pred=False):
        self.pred = pred
        self.max_len = 1000
        self.data_X = data_X
        self.map_AA = self.getAAmap()

        if not pred:
            self.data_Y = data_Y
            self.map_EC = self.getECmap(explainECs)
        
    
    def __len__(self):
        return len(self.data_X)
    
    
    def getAAmap(self):
        aa_vocab = [' ', 'A', 'C', 'D', 'E', 
                    'F', 'G', 'H', 'I', 
                    'K', 'L', 'M', 'N', 
                    'P', 'Q', 'R', 'S',
                    'T', 'V', 'W', 'Y', ]
        map = {}
        for i, char in enumerate(aa_vocab):
            baseArray = i # use this line for embedding instead of the above three
            map[char] = baseArray
        return map
    
    
    def getECmap(self, explainECs):
        ec_vocab = list(set(explainECs))
        ec_vocab.sort()
        map = {}
        for i, ec in enumerate(ec_vocab):
            baseArray = np.zeros(len(ec_vocab))
            baseArray[i] = 1
            map[ec] = baseArray
        return map


    def convert2onehot_seq(self, single_seq):
        single_onehot = np.zeros((self.max_len), dtype=np.int64)
        for i, x in enumerate(single_seq):
            single_onehot[i] = np.asarray(self.map_AA[x])
        return single_onehot
    
    
    def convert2onehot_EC(self, EC):
        map_EC = self.map_EC
        single_onehot = np.zeros(len(map_EC))
        for each_EC in EC:
            single_onehot += map_EC[each_EC]
        return single_onehot
    
    
    def __getitem__(self, idx):
        x = self.data_X[idx]
        x = self.convert2onehot_seq(x)

        if self.pred:
            return x

        y = self.data_Y[idx]
        y = self.convert2onehot_EC(y)
        y = y.reshape(-1)
        return x, y


######

class EnzymeDataset(Dataset):
    def __init__(self, data_X, data_Y, pred=False):
        self.pred = pred
        self.data_X = data_X
        self.map_AA = self.getAAmap()

        if not pred:
            self.data_Y = data_Y
        
    
    def __len__(self):
        return len(self.data_X)
    
    
    def getAAmap(self):
        aa_vocab = ['A', 'C', 'D', 'E', 
                    'F', 'G', 'H', 'I', 
                    'K', 'L', 'M', 'N', 
                    'P', 'Q', 'R', 'S',
                    'T', 'V', 'W', 'Y', ]
        map = {}
        for i, char in enumerate(aa_vocab):
            baseArray = np.zeros(len(aa_vocab))
            baseArray[i] = 1 # use this line for embedding instead of the above three
            map[char] = baseArray
        return map

        
    def convert2onehot_seq(self, single_seq, max_seq=1000):
        single_onehot = np.zeros((max_seq, len(self.map_AA)))
        for i, x in enumerate(single_seq):
            single_onehot[i] = np.asarray(self.map_AA[x])
        return single_onehot


    def convert2int(self, label):
        return np.asarray(label, dtype=np.float)
    
    
    def __getitem__(self, idx):
        x = self.data_X[idx]
        x = self.convert2onehot_seq(x)
        x = x.reshape((1,) + x.shape)

        if self.pred:
            return x

        y = self.data_Y[idx]
        y = self.convert2int(y)
        y = y.reshape(-1)
        return x, y


# class EnzymeEmbedDataset(Dataset):
#     def __init__(self, data_X, data_Y, pred=False):
#         self.pred = pred
#         self.data_X = data_X
#         self.map_AA = self.getAAmap()

#         if not pred:
#             self.data_Y = data_Y
        
    
#     def __len__(self):
#         return len(self.data_X)
    
    
#     def getAAmap(self):
#         aa_vocab = ['A', 'C', 'D', 'E', 
#                     'F', 'G', 'H', 'I', 
#                     'K', 'L', 'M', 'N', 
#                     'P', 'Q', 'R', 'S',
#                     'T', 'V', 'W', 'Y', ]
#         map = {}
#         for i, char in enumerate(aa_vocab):
#             baseArray = np.zeros(len(aa_vocab))
#             baseArray[i] = 1 # use this line for embedding instead of the above three
#             map[char] = baseArray
#         return map

        
#     def convert2onehot_seq(self, single_seq, max_seq=1000):
#         single_onehot = np.zeros((max_seq), dtype=np.int64)
#         for i, x in enumerate(single_seq):
#             single_onehot[i] = np.asarray(self.map_AA[x])
#         return single_onehot


#     def convert2int(self, label):
#         for y in label:
#             return np.asarray(y, dtype=np.float)
    
    
#     def __getitem__(self, idx):
#         x = self.data_X[idx]
#         x = self.convert2onehot_seq(x)
#         x = x.reshape(1, -1)

#         if self.pred:
#             return x

#         y = self.data_Y[idx]
#         y = self.convert2int(y)
#         y = y.reshape(-1)
#         return x, y



class EnzymeEmbedDataset(Dataset):
    def __init__(self, data_X, data_Y, explainECs, pred=False):
        self.pred = pred
        self.max_len = 1000
        self.data_X = data_X
        self.map_AA = self.getAAmap()

        if not pred:
            self.data_Y = data_Y
        
    
    def __len__(self):
        return len(self.data_X)
    
    
    def getAAmap(self):
        aa_vocab = [' ', 'A', 'C', 'D', 'E', 
                    'F', 'G', 'H', 'I', 
                    'K', 'L', 'M', 'N', 
                    'P', 'Q', 'R', 'S',
                    'T', 'V', 'W', 'Y', ]
        map = {}
        for i, char in enumerate(aa_vocab):
            baseArray = i # use this line for embedding instead of the above three
            map[char] = baseArray
        return map


    def convert2onehot_seq(self, single_seq):
        single_onehot = np.zeros((self.max_len), dtype=np.int64)
        for i, x in enumerate(single_seq):
            single_onehot[i] = np.asarray(self.map_AA[x])
        return single_onehot
    
    def convert2int(self, label):
        for y in label:
            return np.asarray(y, dtype=np.float)
    
    
    def __getitem__(self, idx):
        x = self.data_X[idx]
        seq_len = len(x)
        x = self.convert2onehot_seq(x)
        mask = torch.zeros(x.shape)
        mask[seq_len:].fill_(1.0)

        if self.pred:
            return x, mask

        y = self.data_Y[idx]
        y = self.convert2int(y)
        y = y.reshape(-1)
        return x, mask, y



class DeepECDataset(Dataset):
    def __init__(self, data_X, data_Y, explainECs, tokenizer_name='Rostlab/prot_bert_bfd', max_length=1000, pred=False):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, do_lower_case=False)
        self.max_length = max_length
        self.data_X = data_X
        self.data_Y = data_Y
        self.pred = pred
        self.map_EC = self.getECmap(explainECs)
        
        
    def __len__(self):
        return len(self.data_X)
    
    
    def getECmap(self, explainECs):
        ec_vocab = list(set(explainECs))
        ec_vocab.sort()
        map = {}
        for i, ec in enumerate(ec_vocab):
            baseArray = np.zeros(len(ec_vocab))
            baseArray[i] = 1
            map[ec] = baseArray
        return map
    

    def convert2onehot_EC(self, EC):
        map_EC = self.map_EC
        single_onehot = np.zeros(len(map_EC))
        for each_EC in EC:
            single_onehot += map_EC[each_EC]
        return single_onehot
    
    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
            
        seq = " ".join(str(self.data_X[idx]))
        seq = re.sub(r"[UZOB]", "X", seq)
        
        seq_ids = self.tokenizer(seq, truncation=True, padding='max_length', max_length=self.max_length)
        
        sample = {key: torch.tensor(val) for key, val in seq_ids.items()}
        labels = self.data_Y[idx]
        labels = self.convert2onehot_EC(labels)
        labels = labels.reshape(-1)
        sample['labels'] = torch.tensor(labels)
        return sample