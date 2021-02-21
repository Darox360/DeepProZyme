#DeepEC reconstruction
##Procedure

**Note**: 
This source code was developed in Linux, and has been tested in Ubuntu 16.06 with Python 3.7.

1. Clone the repository

        git clone https://anlito@bitbucket.org/anlito/deepec_2.git

2. Create and activate virtual environment

        conda env create -f environment.yml
        conda activate torch_env


##Example


- Train CNN1

        python cnn1_training.py -o ./output/cnn1 -g cuda:0 -e 30 -b 64 -r 1e-4 -p 3 -c checkpoint.pt 

        python cnn_focal_loss_training.py -i ./Dataset/DeepEC_v2_input_sequences.fa -o ./output/deepec_fl_04 -g cuda:3 -e 50 -b 512 -r 1e-5 -p 5 -third False

- Train CNN2

        python cnn_training.py -i ./Dataset/processedUniRefSeq.fasta -o ./output/ec7_cnn3_01 -g cuda:0 -e 30 -b 128 -r 1e-3 -p 5 -third False

- Train CNN3

        python cnn_training.py -i ./Dataset/DeepEC_v2_input_sequences.fa -o ./output/deepec_v2_01 -g cuda:0 -e 50 -b 128 -r 1e-3 -p 5 -third False
        python cnn_training.py -o ./output/uniprot_08 -e 30 -p 5 -b 1024 -r 1e-3 -g cuda:0 -i ./Dataset/uniprot_dataset.fa

- Evaluate DeepEC

        python deepec_evaluate.py -o ./output/deepec_evaluation -g cuda:0 -b 1024 -c1 ./output/cnn1_01/checkpoint.pt -c2 ./output/ec7_cnn2_01/checkpoint.pt -c3 ./output/ec7_cnn3_03/checkpoint.pt -t ./Dataset/processedUniRefSeq.fasta


- Run DeepEC predicion

        python cnn_running.py -enz ./Dataset/example_tf.fasta -ckpt ./output/ec7_cnn3_03/checkpoint.pt -o ./output/ec7_cnn3_03/prediction_result -g cuda:0


- Train short transformer

        python transformer_training.py -i ./Dataset/input_dataset.fa -o ./output/transformer_short_04 -e 50 -p 5 -b 256 -r 1e-3 -g cuda:2 

- Run short transformer

        python transformer_running.py -i ./Dataset/analysis_sequences/substrate_change_seqs.fa -o ./output/transformer_short_09 -ckpt ./output/transformer_short_09/checkpoint.pt -g cuda:0