from colorama import Fore, Back, Style


def format_dict_result(thedict):
    dict_results = ""
    for k in thedict.keys():
        dict_results += (
            f"{Fore.LIGHTCYAN_EX}{k}: {Fore.WHITE}{thedict[k]}{Style.RESET_ALL}\n"
        )
    return dict_results
