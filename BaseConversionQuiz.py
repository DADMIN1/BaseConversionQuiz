import random
import tkinter
# import tkinter.ttk as ttk


base_ranges = {
    "B": (0,  2),
    "D": (0, 10),
    "H": (0, 16),
}


def CheckAnswer(inputnumber:str, answer:int, input_mode="B"):
    base = base_ranges[input_mode][1]
    return int(inputnumber, base) == answer


assert CheckAnswer("101", 5)
assert CheckAnswer("1011", 11)
assert CheckAnswer("0F", 15, input_mode="H")
assert CheckAnswer("FF", 255, input_mode="H")


def GenerateQuiz(mode="B", max_places=4, min_places=1, batch_size=5) -> dict[str:int]:
    rmin, rmax = base_ranges[mode]
    choices = range(rmin,rmax)
    if mode == "H": choices = [hex(i).removeprefix('0x').upper() for i in choices]
    
    def generate_number():
        return ''.join(str(random.choice(choices)) for _ in range(random.choice(range(min_places, max_places+1)))).zfill(max_places)
    
    question_set = { generate_number() for _ in range(batch_size) }
    question_set.discard('0'.zfill(max_places))  # removing all-zero entry if it exists
    
    # finding number of possible combinations (matters for binary mostly) 
    upper_bound = max(batch_size, (rmax ** max_places)-(rmin ** min_places))
    target_size = min(batch_size, upper_bound)
    diff = target_size - len(question_set)
    
    retry_count = 0
    while diff > 0: # trying to meet target_size
        if retry_count > 100: break
        new_questions = { generate_number() for _ in range(diff) }
        new_questions.discard('0'.zfill(max_places))
        question_set.update(new_questions)
        diff = target_size - len(question_set)
        retry_count += 1
    
    # answers are in decimal
    return { n : int(n, base_ranges[mode][1]) for n in question_set }


settings = {
    "mode": "Binary",  # Binary or Hexadecimal
    "swapped": False,  # questions are in decimal, answers in binary/hex
    "digits_min":  1,
    "digits_max":  4,
    "batch_size":  5,
}

answer_entries = []
answer_answers = []

def PopulateBottomFrame(quiz: dict, bottomframe):
    for child in bottomframe.pack_slaves():
        child.destroy()
    answer_entries.clear()
    answer_answers.clear()
    questionframe = tkinter.Frame(bottomframe)
    questionframe.pack(side="left")
    for i, (question, answer) in enumerate(quiz.items()):
        line = tkinter.Frame(questionframe)
        line.pack()
        tkinter.Label(line, text=question+": ").pack(anchor="nw", side="left")
        entry = tkinter.Entry(line)
        entry.contents = tkinter.StringVar()
        # entry.contents.set(0)
        entry["textvariable"] = entry.contents
        entry.pack(side="left")
        resulttext = tkinter.Label(line)
        resulttext.pack(side="right")
        answer_entries.append((entry, resulttext))
        answer_answers.append(answer)
    return


if __name__ == "__main__":
    toplevel = tkinter.Tk()
    toplevel.title("Base Conversion Quiz")
    topframe = tkinter.Frame(toplevel)
    bottomframe = tkinter.Frame(toplevel)
    topframe.pack(side="top")
    bottomframe.pack(side="bottom")
    
    quiz = GenerateQuiz()
    PopulateBottomFrame(quiz, bottomframe)
    
    settings_stringvars = { k: tkinter.StringVar() for k in settings.keys() }
    for k,v in settings.items(): settings_stringvars[k].set(v)
    
    tkinter.OptionMenu(topframe, settings_stringvars["mode"], "Binary", "Hexadecimal").pack(side="left")
    for setting in ("digits_min", "digits_max", "batch_size"):
        dropdown = tkinter.OptionMenu(topframe, settings_stringvars[setting], settings[setting], *range(2,17)) #command=lambda event: print("callback")
        tkinter.Label(topframe, text=setting+": ").pack(side="left")
        dropdown.pack(side="left")
        #dropdown["command"] = lambda event: print(dropdown["value"])
        #stringvars[setting].trace("w", lambda x, y, z: print(f"callback {x}, {y}, {z}"))
    
    # TODO: toggle for decimal mode
    
    # for setting, val in settings.items():
    #     tkinter.Label(topframe, text=setting).pack(anchor="n", side="left")
    #     entry = tkinter.Entry(topframe)
    #     entry.contents = tkinter.StringVar()
    #     entry.contents.set(val)
    #     entry["textvariable"] = entry.contents
    #     entry.pack(anchor="n", side="left")
    
    def Generate():
        for setting, stringvar in settings_stringvars.items():
            match setting:
                case "mode": settings[setting] = stringvar.get()
                case "swapped": settings[setting] = bool(stringvar.get()) 
                case "digits_min" | "digits_max" | "batch_size": settings[setting] = int(stringvar.get())
                case _: settings[setting] = stringvar.get()
        settings["digits_min"] = min(settings["digits_min"], settings["digits_max"])
        settings["digits_max"] = max(settings["digits_min"], settings["digits_max"])
        settings_stringvars["digits_min"].set(str(settings["digits_min"]))
        settings_stringvars["digits_max"].set(str(settings["digits_max"]))
        # print(settings)
        global quiz
        quiz = GenerateQuiz(settings["mode"][0], settings["digits_max"], settings["digits_min"], settings["batch_size"])
        PopulateBottomFrame(quiz, bottomframe)
        return
    
    def Check():
        for i, (entry, resulttext) in enumerate(answer_entries):
            #if not entry.contents.get(): resulttext["text"] = ""
            #if CheckAnswer(entry.contents.get(), answer_answers[i], settings["mode"][0]):
            if entry.contents.get() == "": resulttext["text"] = ""
            elif entry.contents.get() == str(answer_answers[i]): resulttext["text"] = "Correct"
            else: resulttext["text"] = "Incorrect"
        return
    
    def ShowAnswers():
        for i, (entry, resulttext) in enumerate(answer_entries):
            resulttext["text"] = answer_answers[i]
        return
    
    tkinter.Button(topframe, text="Generate", command=Generate).pack(side="left")
    tkinter.Button(topframe, text="Check", command=Check).pack(side="left")
    tkinter.Button(topframe, text="Answers", command=ShowAnswers).pack(side="left")
    
    toplevel.mainloop()
