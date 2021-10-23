import sys, getopt, os
import csv, json

def transjson(src, tar):
    jfile = open(src, 'r', encoding = 'utf8')
    cfile = open(tar, 'w', newline = '')
    jdict = json.load(jfile)            #load->json文件, loads->json字符串，转换为python对象
    writer = csv.writer(cfile)
    writer.writerow(jdict.keys())
    writer.writerow(jdict.values())
    jfile.close()
    cfile.close()

def transcsv(src, tar):
    cfile = open(src, 'r', newline = '')
    jfile = open(tar, 'w', encoding = 'utf8')
    reader = csv.DictReader(cfile)
    rows = list(reader)
    json.dump(rows, jfile)
    cfile.close()
    jfile.close()

def main(argv):
    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print ('cliarg.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print ('cliarg.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    arg1 = os.path.splitext(inputfile)
    arg2 = os.path.splitext(outputfile)

    inputfilename, inputtype = arg1
    outputfilename, outputtype = arg2

    if inputtype == '.json' and outputtype == '.csv':
        transjson(inputfile, outputfile)
        print(inputfilename + inputtype + ' ' + outputfilename + outputtype)
    elif inputtype == '.csv' and outputtype == '.json':
        transcsv(inputfile, outputfile)
        print(inputfilename + inputtype + ' ' + outputfilename + outputtype)

if __name__ == "__main__":
    main(sys.argv[1:])