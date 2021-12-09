import textract
import pandas as pd
import dateparser
import glob


def text_to_arr(file_path:str):
    print(file_path)
    text = textract.process(file_path).decode().split('\n')

    # scrap front part
    text = text[12:]

    # scrap zusammenfassung
    text = text[:text.index('\x0cZUSAMMENFASSUNG')]

    # remove empty strings
    text = list(filter(None, text))
    text = list(filter(None, text))

    num_of_bookings = ' '.join(text).count("€")
    # remove whitespace
    for i in range(len(text)):
        if text[i].startswith("\x0c"):
            text[i] = text[i][1:]



    # remove bottom "Erstellt am" from list
    text = [item for item in text if "Erstellt am" not in item]

    # remove empty "IBAN: BIC"
    text = [item for item in text if "IBAN: BIC:" not in item]

    for i in range(len(text)):
        if " €" in text[i] and text[i-1] == "Kartenzahlung":
            tmp = text[i-1]
            text[i-1] = text[i]
            text[i] = tmp

    # get all dates from list
    possible_dates = ["MONTAG,", "DIENSTAG,", "MITTWOCH,","DONNERSTAG,","FREITAG,","SAMSTAG,","SONNTAG,"]
    dates = [text.index(item) for item in text if any(dates in item for dates in possible_dates)]

    text_dict = {}

    # create dict by dates
    for i in range(len(dates)):
        end = 0
        print(i)
        if i == len(dates)-1:
            end = len(text)
        else:
            end = dates[i+1]

        text_dict[text[dates[i]]] = text[dates[i]+1:end]

    # split text by every transaction
    for key in text_dict.keys():
        s = text_dict[key]
        demo_list = []
        for i in range(len(s)):
            if s[i] == "Überweisung" or s[i] == "Lastschrift":
                if "€" not in s[i-1]:
                    tmp_list = []
                    tmp_list.append(s[i-1])
                    tmp_list.append(s[i+3])
                    tmp_list.extend(s[i:i+3])
                    demo_list.append(tmp_list)
                else:
                    demo_list.append(s[i-2:i+3])
            if s[i] == "Kartenzahlung":
                demo_list.append(s[i-2:i+1])
        text_dict[key] = demo_list
        
    # parse string date
    correct_date_dict = {}
    for key in text_dict.keys():
        correct_date = dateparser.parse(key, languages=["de"]).strftime("%d/%m/%Y")
        correct_date_dict[correct_date] = text_dict[key]

    # flatten list append date at beginning
    final_list = []
    for key in correct_date_dict.keys():
        for transaction in correct_date_dict[key]:
            transaction_copy = transaction.copy()
            transaction_copy.insert(0, key)
            # pad to six entries
            transaction_copy += [None] * (6 - len(transaction_copy))
            final_list.append(transaction_copy)

    print(num_of_bookings, len(final_list))
    assert num_of_bookings == len(final_list)
    # convert list to dataframe
    column_names = ["date", "merchant", "value", "type", "IBANBIC", "description"]
    df = pd.DataFrame(final_list, columns=column_names)
    return df

pdfs = glob.glob("pdfs/*.pdf")
df_list = []
for pdf in pdfs:
    df = text_to_arr(pdf)
    print(df)
    df_list.append(df)

df = pd.concat(df_list, ignore_index=True)

# export dataframe
df.to_csv("output.csv", index=False)
