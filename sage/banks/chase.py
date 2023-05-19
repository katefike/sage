@dataclass(init=True, repr=True)
class Chase:
    raw_amount_regex: "(?<=\$)(.*)(?= transaction)"