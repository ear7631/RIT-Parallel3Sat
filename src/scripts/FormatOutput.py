import os
import sys


# dictionaries: tag --> mapping
# mapping: size --> inner mapping
# inner: proc ---> list of results

# ex:
# dictionaries["goutTSESmp"][23][8] --> list of results for goutTSESmp, size 23, 8 processors
dictionaries = {}

# sequential is different
# size -> results
sequential = {}
e_sequential = {}

files = {}

VARIABLE_CLAUSES = False

SIZE_RANGE = 5

tags = ("outTSSmp", "outTSESmp", "goutTSSmp", "goutTSESmp", "doutTSSmp", "doutTSESmp")


def generate_output_file(tag):
    f = files[tag]
    d = dictionaries[tag]

    sizes = sorted(d.keys())
    for size in sizes:
        procs = sorted(d[size].keys())
        for proc in procs:
            line = str(size) + " " + str(proc) + " "
            results = None

            if proc == 0:
                if "TSE" in tag:
                    results = e_sequential[size]
                else:
                    results = sequential[size]
            else:
                results = d[size][proc]

            if results == []:
                continue

            for result in results:
                line = line + str(result) + " "
            line = line.strip()
            f.write(line + "\n")

    # Do the closing bit to translate the size
    for size in range(1, SIZE_RANGE + 1):
        if VARIABLE_CLAUSES:
            f.write("n " + str(size) + " " + str(size * 1000) + "\n")
        else:
            f.write("n " + str(size) + " " + str(size + 22) + "\n")


def grab_time_standard(filename):
    f = open(filename)
    content = f.read().strip()
    f.close()
    lines = content.split("\n")
    time_line = lines[-1]
    time = time_line[: time_line.find("msec")]
    time = time.strip()
    return time


def parse_sequential(filename, tag):
    i = len(tag)
    size = filename[i: filename.find('-')]
    time = grab_time_standard(filename)

    if "TSE" in tag:
        e_sequential[int(size)].append(time)
    else:
        sequential[int(size)].append(time)


def parse_smp(filename, tag):
    i = len(tag)
    suffix = filename[i:]
    proc = suffix[0]
    size = suffix[1]
    time = grab_time_standard(filename)
    dictionaries[tag][int(size)][int(proc)].append(time)


def extractFromFile(filename):
    if "output_" in filename:
        return

    # sequential
    tag = ""
    if "outTSSeq" in filename:
        tag = "outTSSeq"
    elif "outTSESeq" in filename:
        tag = "outTSESeq"

    # guided
    elif "gout" in filename:
        if "goutTSSmp" in filename:
            tag = "goutTSSmp"
        elif "goutTSESmp" in filename:
            tag = "goutTSESmp"

    # dynamic
    elif "dout" in filename:
        if "doutTSSmp" in filename:
            tag = "doutTSSmp"
        elif "doutTSESmp" in filename:
            tag = "doutTSESmp"

    # no scheduler
    elif "outTSSmp" in filename:
        tag = "outTSSmp"
    elif "outTSESmp" in filename:
        tag = "outTSESmp"

    # call the parse functions
    if "Seq" in tag:
        parse_sequential(filename, tag)
    elif "Smp" in tag:
        parse_smp(filename, tag)
    else:
        print "UNHANDLED FILE NAME: " + filename


def main():
    global VARIABLE_CLAUSES

    if len(sys.argv) == 1:
        print "Usage: python FormatOutput [l | c]"
        print "      l - literals"
        print "      c - clauses "
        sys.exit()
    elif len(sys.argv) > 1:
        if sys.argv[1] == "c":
            VARIABLE_CLAUSES = True
        elif sys.argv[1] == "l":
            VARIABLE_CLAUSES = False
        else:
            print "Usage: python FormatOutput [c | l]"
            sys.exit()

    for tag in tags:
        dictionaries[tag] = {}
        files[tag] = open("output_" + tag + ".txt", "w")

    for size in range(1, SIZE_RANGE + 1):
        sequential[size] = []
        e_sequential[size] = []

        for key in dictionaries:
            dictionaries[key][size] = {}

        for processors in range(9):
            for key in dictionaries:
                dictionaries[key][size][processors] = []

    for root, dirs, file_list in os.walk('.'):
        for f in file_list:
            extractFromFile(f)

    for tag in tags:
        generate_output_file(tag)


if __name__ == '__main__':
    main()
