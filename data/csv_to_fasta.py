import csv

def csv_to_fasta(csv_file_path, fasta_file_path):
    with open(csv_file_path, 'r') as csv_file, open(fasta_file_path, 'w') as fasta_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        for row in csv_reader:
            identifier = row['Entry']
            sequence = row['Sequence']
            fasta_file.write(f">{identifier}\n{sequence}\n")

# 使用函数
csv_file_path = 'new.csv'  # 你的CSV文件路径
fasta_file_path = 'new.fa'  # 你想要保存的FASTA文件路径
csv_to_fasta(csv_file_path, fasta_file_path)
