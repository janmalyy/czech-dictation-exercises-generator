import random


def get_phrases_list(file_name):
    """
    :param file_name: název textového souboru se slovními spojeními Každé slovní spojení na novém řádku. Občas na řádku více spojení oddělených tabulátorem.
    :return: list stringů se slovními spojeními. Pokud více spojení, jsou v listu.
    """
    with open(file_name, "r", encoding="utf-8") as file:
        lines = file.readlines()
    phrases_list = []
    for line in lines:
        if "\t" in line:
            phrases_list.append(line.strip().split("\t"))
        else:
            phrases_list.append(line.strip())
    return phrases_list


def choose_n_phrases(diff, phrases_list, n):
    """
    :param diff: obtížnost diktátu, 0-lehčí, 1-těžší, 2-mix
    :param phrases_list: list stringů se slovními spojeními. Pokud více spojení, jsou v listu. Z nich se vybírá.
    :param n: kolik slovních spojení se má vybrat
    :return: vybraná slovní spojení
    """
    if diff != 2:
        diff_0 = []
        diff_1 = []
        chosen = []
        for i in range(len(phrases_list)):  # separate 0 and 1 difficulty
            if phrases_list[i][-1] == "0":
                diff_0.append(phrases_list[i][:-1])  # without the difficulty level
            else:
                diff_1.append(phrases_list[i][:-1])

        if diff == 0:
            if len(diff_0) <= n:
                chosen.extend(diff_0)       # extend must be used, not append, because I want to add the phrases themselves, not the list with phrases
                chosen.extend(random.sample(diff_1, n - len(diff_0)))
            else:
                chosen.extend(random.sample(diff_0, n))

        else:  # diff = 1
            if len(diff_1) <= n:
                chosen.extend(diff_1)
                chosen.extend(random.sample(diff_0, n - len(diff_1)))
            else:
                chosen.extend(random.sample(diff_1, n))

    else:
        chosen = random.sample(phrases_list, n)

    # tady řeším, pokud jsem si při random.sample náhodou vybral nějaký list
    for i in range(len(chosen)):
        if type(chosen[i]) == list:
            if chosen[i][-1] == "0" or chosen[i][-1] == "1":  # odstraňuju difficulty, pokud diff == 2
                chosen[i].remove(chosen[i][-1])
            only_one = random.choice(chosen[i])
            chosen[i] = only_one
    return chosen


def choose_n_phrases_in_order(phrases_list, n):
    """
    vybere n frází, zachová jejich pořadí
    :param phrases_list: list stringů se slovními spojeními
    :param n: kolik se má vybrat frází
    :return: vybraná slovní spojení
    """
    chosen = []
    while len(phrases_list) != n:
        x = random.randint(0, len(phrases_list)-1)
        phrases_list.remove(phrases_list[x])
    for i in range(len(phrases_list)):
        chosen.append(random.choice(phrases_list[i]))
    return chosen


def generate_one_text(phrases, length, model, client, in_order=False):
    """
    :param phrases: seznam stringů, slovní spojení, ze kterých budu tvořit
    :param length: požadovaná délka vygenerovaného textu
    :param model: obvykle gpt-3.5-turbo nebo gpt-4
    :param client: jen aby se nevytvářel furt znova
    :param in order: True, pokud se jedná o cvičení na shodu; drobně upraví vstupní text
    :return: vygenerovaný text jako string
    """
    content = f"Create a text in Czech of exactly {length} words." \
              f"Use each of the phrases in the given list only and just once in the text: {phrases}." \
              f"The sentences are short. The text contains only simple and understandable words." \
              f"The sentences build on each other to form one continuous narrative."
    if in_order:
        content = f"Create a text in Czech of exactly {length} words." \
                  f"Use each of the phrases in the given list only and just once in the text: {phrases}." \
                  f"Use the phrases in the given order, develop them in order to make sense." \
                  f"The sentences are short. The text contains only simple and understandable words." \
                  f"The sentences build on each other to form one continuous narrative."

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a text generator maximally aligned with given instructions."},
            {"role": "user", "content": content}
        ])
    return completion.choices[0].message.content


def generate_n_texts(phrases, length, model, client, in_order=False, n_of_texts=3):
    """
    just calls n times function generate_one_text and assemble the texts into list of strings, which is then returned
    """
    generated_texts = []
    for i in range(n_of_texts):
        generated_texts.append(generate_one_text(phrases, length, model, client, in_order=in_order))
    return generated_texts