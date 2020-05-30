import re

def parse(text):
    index = -1
    uppertitle = text.upper()

    if "PACK OF" in uppertitle:
        index = uppertitle.find("PACK OF")
        return int(isolate_pcs_reversed(text[index + 7 : len(uppertitle)].strip()))
    if "BOX OF" in uppertitle:
        index = uppertitle.find("BOX OF")
        return int(isolate_pcs_reversed(text[index + 7: len(uppertitle)].strip()))
    if "LOT OF" in uppertitle:
        index = uppertitle.find("LOT OF")
        return int(isolate_pcs_reversed(text[index + 7: len(uppertitle)].strip()))

    if "PCS" in uppertitle:
        index = uppertitle.find("PCS")
    elif "PACK" in uppertitle:
        index = uppertitle.find("PACK")
    elif "PC" in uppertitle:
        index = uppertitle.find("PC")
    elif "PK" in uppertitle:
        index = uppertitle.find("PK")
    elif "QTY" in uppertitle:
        index = uppertitle.find("QTY")
    elif "PIECE" in uppertitle:
        index = uppertitle.find("PIECE")

    if index == -1:
        return 1
    else:
        #print(text[0:index].strip())
        return int(isolate_pcs(text[0:index].strip()))

def isolate_pcs(text):
    if " " in text:
        text_pieces = text.split(" ")
        for x in range(len(text_pieces) - 1, -1, -1):
            text_pieces[x] = re.sub("[^/\-0-9]", '', text_pieces[x])
        for x in range(len(text_pieces) - 1, -1, -1):
            if text_pieces[x] == "":
                text_pieces.pop(x)
            else:
                return get_first_pcs(text_pieces[x])
    else:
        text = re.sub("[^/\-0-9]", '', text)
        return get_first_pcs(text)

def isolate_pcs_reversed(text):
    if " " in text:
        text_pieces = text.split(" ")
        for x in range(len(text_pieces) - 1, -1, -1):
            text_pieces[x] = re.sub("[^/\-0-9]", '', text_pieces[x])
        for x in range(0, len(text_pieces)):
            if text_pieces[x] == "":
                text_pieces.pop(x)
            else:
                return get_first_pcs(text_pieces[x])
    else:
        return get_first_pcs(text)

def get_first_pcs(text):
    if "/" in text:
        pieces = text.split("/")
        for x in range(0, len(pieces)):
            try:
                int(pieces[x])
                return pieces[x]
            except ValueError:
                continue
        return 1
    elif "-" in text:
        pieces = text.split("-")
        for x in range(0, len(pieces)):
            try:
                int(pieces[x])
                return pieces[x]
            except ValueError:
                continue
        return 1
    else:
        try:
            int(text)
            return text
        except ValueError:
            return 1

# def clean_pcs(text):
#     empty = []
#     if " " in text:
#         text_array = text.split(" ")
#         for x in range(len(text_array) - 1, -1, -1):
#             text_array[x] = re.sub("[^/\-0-9]", '', text_array[x])
#             if text_array[x] == "":
#                 text_array.pop(x)
#             elif "/" or "-" in text_array[x]:
#                 pcsstring = clean_multiple_pcs(text_array[x])
#                 return int(pcsstring)
#         try:
#             pcsstring = text_array[len(text_array) - 1]
#         except IndexError:
#             return 1
#     else:
#         pcsstring = re.sub("[^/\-0-9]", '', text)
#         if pcsstring == "":
#             return 1
#     if "/" or "-" in pcsstring:
#         pcsstring = clean_multiple_pcs(pcsstring)
#     else:
#         if pcsstring != " ":
#             return int(pcsstring)
#         else:
#             return 1
#     return int(pcsstring)
#
# def clean_multiple_pcs(text):
#     if "/" in text:
#         pieces = text.split("/")
#         for x in range(0, len(pieces)):
#             try:
#                 int(pieces[x])
#                 return pieces[x]
#             except ValueError:
#                 continue
#     elif "-" in text:
#         pieces = text.split("-")
#         for x in range(0, len(pieces)):
#             try:
#                 int(pieces[x])
#                 return pieces[x]
#             except ValueError:
#                 continue
#     else:
#         return 1