import pandas as pd
import sys
import json
import re
from Bio import Phylo
from io import StringIO
# sepicify query jplacer path
jplace_path = sys.argv[1]
# load query jplacer file by json package
with open(jplace_path, "r") as jplace_file:
    jplace_dic = json.load(jplace_file)

# sepicify target taxon group
#target_set = set(['Pimascovirales',
#'Asfuvirales',
#'Imitervirales',
#'Algavirales',
#'Chitovirales',
#'Pandoravirales'
#])

target_set = set(["AF_01","IM_08","PM_10","IM_16","incertae_sedis","IM_01","IM_09","PV_05","IM_06","IM_12","AG_03","PM_01","AG_04","IM_07","AG_01","PV_03","IM_13","IM_14","IM_18","PM_03","PX_01","PM_02","AG_02","PV_04","PM_07","PM_05","PM_04","PM_06","AF_02","PM_08","IM_02","PV_02","PM_09"])

# load reference phylogenetic tree
tree = Phylo.read(StringIO(jplace_dic["tree"]), "newick")


# define position patten Regular Expression
name_position_pattern = re.compile(r"([-\w\.@]*):[\d\.\-e]+\{(\d+)\}")

########name_position_pattern = re.compile(r"([-\w\.]*):")
# find all name_possition (including terminal and nonterminal positions)
name_position_tuple_arr = name_position_pattern.findall(jplace_dic["tree"])

# make terminal_position_dic
terminal_position_dic = dict((name_position_tuple[1], name_position_tuple[
                             0]) for name_position_tuple in name_position_tuple_arr if name_position_tuple[0] != "")
#len(terminal_position_dic)

def get_nonterminal_position(nonterminal_clade):
    def remove_mark(x): return x.replace("{", "").replace("}", "")
    name_arr = [terminal_position_dic[remove_mark(
        clade.name)] for clade in nonterminal_clade.get_terminals()]
    return (remove_mark(nonterminal_clade.name), name_arr)

nonterminal_position_gen = (get_nonterminal_position(
    nonterminal_clade) for nonterminal_clade in tree.get_nonterminals())

# merge terminal and nonterminal into position_name_dic
# key:postion number in string format
# value:names of all reference sequences under that position
position_name_dic = {position: [name]
                     for position, name in terminal_position_dic.items()}
position_name_dic.update(nonterminal_position_gen)



def Gen_qname_qcate(jplace_dic):
    for placement_dic in jplace_dic["placements"]:
        query_name_arr = [nm[0]for nm in placement_dic["nm"]]
        query_position = str(placement_dic["p"][0][1])
        query_cate_set = set(cate_name.split("@")[0] for cate_name in position_name_dic[query_position])
        for query_name in query_name_arr:
            yield (query_name, query_cate_set)


qname_qcate_dic = dict(Gen_qname_qcate(jplace_dic))



# pick titles for each family
for target_family in sorted(target_set):
    with open(jplace_path+"."+target_family, "w") as output_file:
        output_name_arr = [qname for qname, qcate in qname_qcate_dic.items() if qcate == {
            target_family}]
        output_file.write("\n".join(output_name_arr))

# pick titles for all NCLDV
with open(jplace_path+".NCLDV", "w") as output_file:
    output_name_arr = [qname for qname, qcate in qname_qcate_dic.items() if qcate <= target_set]
    output_file.write("\n".join(output_name_arr))
