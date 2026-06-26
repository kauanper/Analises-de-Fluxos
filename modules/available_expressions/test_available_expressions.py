import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.core.core import parse_input, print_result
from modules.available_expressions.available_expressions import run_available_expressions

def main():
    example_input = [
        "1 2",                
        "i = 0",               
        "res1 = a + b",        
        "2",                   

        "2 1",                 
        "cond1 = i",           
        "3 6",                 

        "3 1",                
        "cond2 = a",           
        "4 5",                 

        "4 2",                 
        "i = i + 1",          
        "res2 = x * y",        
        "2",                   

        "5 3",                 
        "temp = a",            
        "a = 999",             
        "res3 = temp / z",     
        "2",                   
        "6 1",                 
        "final = a + b",       
        "0"     
    ]

    if len(sys.argv) > 1:
        cfg = parse_input(sys.argv[1])
    else:
        cfg = parse_input(example_input)

    result = run_available_expressions(cfg)

    print_result("Available Expressions", result, cfg.block_order)

if __name__ == "__main__":
    main()