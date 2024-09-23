from cron.parser import Parser

if __name__ == "__main__":
    try:
        cron_expression = input("Enter cron expression: ")
        parser = Parser(cron_expression)
        result = parser.split_expression()
        parser.print_result(result)
    except Exception as e:
        print(e)