import datetime

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class c_print:
  # If called without static method, simply print the string
  @staticmethod
  def __call__(print_string):
    # print the string
    print(print_string)

  @staticmethod
  def time(print_string):
    # add timestamp to print statements
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S:%f')[:-3]}] {print_string}")

  @staticmethod
  def ok(print_string):
    # print success message
    c_print.time(f"{Colors.OKGREEN}{print_string}{Colors.ENDC}")

  @staticmethod
  def blue(print_string):
    # print info message
    c_print.time(f"{Colors.OKBLUE}{print_string}{Colors.ENDC}")

  @staticmethod
  def cyan(print_string):
    # print info message
    c_print.time(f"{Colors.OKCYAN}{print_string}{Colors.ENDC}")

  @staticmethod
  def warn(print_string):
    # print warning message
    c_print.time(f"{Colors.WARNING}{print_string}{Colors.ENDC}")

  @staticmethod
  def fail(print_string):
    # print error message
    c_print.time(f"{Colors.FAIL}{print_string}{Colors.ENDC}")