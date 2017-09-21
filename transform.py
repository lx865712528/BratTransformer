import glob
import os
import random
import sys


def check_or_creat(path):
    if not os.path.exists(path):
        os.makedirs(path)


def show_help():
    print("USAGE: python transform.py %SOURCE_DATA_ROOT% %TARGET_PATH% %NUM_OF_DOCUMENTS% %FILE_COUNT_LIMIT%")
    print("           %SOURCE_DATA_ROOT%: xxx/trial_data/input")
    print("           %TARGET_PATH%: without last slash")
    print("           %NUM_OF_DOCUMENTS%: document number limit per subtask, suggested 3, unlimited is -1")
    print("           %FILE_COUNT_LIMIT%: CONLL file number limit per document, suggested <= 20, unlimited is -1")


class CONLL():
    def __init__(self):
        self.title = "This is title"
        self.DCT = "YYYY-MM-DD"
        self.ID = "Unique ID"
        self.body = []


def parse_document(document):
    ans = CONLL()
    ans.ID = document[0]
    ans.DCT = document[1][1]
    document = document[2:]
    sentence_segs = []
    body = []
    pos = 0
    while pos < len(document) and document[pos][2] == "TITLE":
        sentence_segs.append(document[pos][1])
        pos += 1
    ans.title = " ".join(sentence_segs)
    prev_sentence_id = "0"
    sentence_segs.clear()
    while pos < len(document):
        cnt_sentence_id = document[pos][0].split(".")[1]
        if cnt_sentence_id != prev_sentence_id and len(sentence_segs) > 0:
            body.append(" ".join(sentence_segs))
            sentence_segs.clear()
        if cnt_sentence_id == "XX":
            break
        sentence_segs.append(document[pos][1])
        prev_sentence_id = cnt_sentence_id
        pos += 1
    for line in body:
        if "NEWLINE" in line:
            segs = line.split("NEWLINE")
            for seg in segs:
                if len(seg) > 0:
                    ans.body.append(seg.strip())
    return ans


def parse(file_path):
    answer = []
    with open(file_path, "r", encoding="utf-8") as f:
        document = []
        for line in f:
            line = line.strip()
            if line.startswith("#begin document"):
                document.clear()
                document.append(line.replace("#begin document", "").strip()[1:-2])
            elif line == "#end document":
                document.append(["XX.XX.XX"])
                answer.append(parse_document(document))
            else:
                document.append(line.split("\t"))
    return answer


def transform(data_root, target_path, limit=-1, content_limit=-1):
    check_or_creat(target_path)
    mids = ["s1", "s2", "s3"]
    for mid in mids:
        target_prefix = "%s/%s" % (target_path, mid)
        check_or_creat(target_prefix)
        paths = glob.glob("%s/%s/CONLL/*.conll" % (data_root, mid))
        if limit > -1:
            paths = random.sample(paths, limit)
        for path in paths:
            content = parse(path)
            file_name = path[path.rfind("/") + 1:path.rfind(".")]
            if content_limit > 0:
                content_chunks = [content[i:i + content_limit] for i in range(0, len(content), content_limit)]
            else:
                content_chunks = [content]
            for id in range(len(content_chunks)):
                with open("%s/%s-%d.txt" % (target_prefix, file_name, id + 1), "w", encoding="utf-8") as f:
                    for i, document in enumerate(content_chunks[id]):
                        if i > 0:
                            f.write("\n")
                        f.write("%s\n" % document.title)
                        f.write("(%s)\tCreated in %s\n" % (document.ID, document.DCT))
                        for line in document.body:
                            f.write("%s\n" % line)
                with open("%s/%s-%d.ann" % (target_prefix, file_name, id + 1), "w", encoding="utf-8") as f:
                    pass


if __name__ == "__main__":
    if len(sys.argv) < 5:
        show_help()
        sys.exit(-1)
    else:
        transform(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
