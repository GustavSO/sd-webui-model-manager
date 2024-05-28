from datetime import datetime

def d_print(text):
    timestamp = datetime.now().strftime('%H:%M:%S:%f')[:-3]
    print(f"\033[94m[Model Manager ({timestamp})]\033[0m {text}")