from cron.constants import minute, hour, day_of_month, month, day_of_week, year
import sys
import re

class InvalidCronRangeError(Exception):
    """
    Custom exception for invalid cron range errors.
    """
    def __init__(self, field_name, field, message="Invalid range for cron field"):
        self.field_name = field_name
        self.field = field
        self.message = message
        super().__init__(f"{message}: {field_name}='{field}'")

class Parser:
    """
    A class to parse and validate cron expressions.
    """
    def __init__(self,expression):
        """
        Initialize the Parser with a cron expression.
        """
        self.expression = expression
        self.field_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
        self.field_name_value_mapping = {"minute":minute, "hour":hour, "day_of_month":day_of_month, "month":month, "day_of_week":day_of_week}
        # Regular expressions to match different cron field patterns
        self.range_pattern = re.compile(r'^\d+-\d+$')
        self.single_value_pattern = re.compile(r'^\d+$')
        self.range_increment_pattern = re.compile(r'^\d+-\d+/(\d+)$|^\*/(\d+)$')


    
    def split_expression(self):
        """
        Split the cron expression into fields and validate them.
        """
        field_vals = self.expression.split()

        if len(field_vals) == 7:

            self.command = " ".join(field_vals[6:])
            self.field_names.append("year")
            self.field_name_value_mapping["year"] = year

            self.cron_dict = dict(zip(self.field_names, field_vals[:6]))
            result_dict = self.validate(self.cron_dict)
            result_dict["command"] = self.command
            return result_dict



        if len(field_vals) != 6:
            raise ValueError(f"Invalid cron Expression must contain 6 fields got {len(field_vals)} fields.")
        
        self.command = " ".join(field_vals[5:])
        self.cron_dict = dict(zip(self.field_names, field_vals[:5]))
        result_dict = self.validate(self.cron_dict)
        result_dict["command"] = self.command
        return result_dict
    
    def validate(self,cron_dict):
        """
        Validate each field in the cron dictionary.
        """
        result_dict = {}

        for field_name, field in cron_dict.items():

            self.special_char_validation(field_name, field)

            if ("," in field and "/" in field) or ("," in field and "-" in field) or ("," in field and "*" in field):
                result_dict[field_name] = self.validate_multiple_conditions(field_name,field)

            else:
                if field == "*":
                    result_dict[field_name] = self.validate_all(field_name)
                elif "/" in field:
                    result_dict[field_name] = self.validate_increments(field_name,field)
                elif "-" in field:
                    result_dict[field_name] = self.validate_range(field_name,field)
                elif "," in field:
                    result_dict[field_name] = self.validate_multiple_commas(field_name,field)
                else:
                    result_dict[field_name] = self.validate_single_value(field_name, field)
        
        return result_dict

    def special_char_validation(self,field_name, field_value):
        """
        Validate that special characters in the field are used correctly.
        """
        allowed_specials = self.field_name_value_mapping[field_name]["supported_special_chars"]

        # Check for invalid multiple occurrences of special characters    
        if "," in field_value:
            parts = field_value.split(',')
            for part in parts:
                for char in part:
                    if char in ["/","*","-"] and part.count(char) > 1:
                        raise ValueError(f"Special character {char} in field {field_value} can occur only once.")
                    
        # Ensure all characters are allowed    
        for char in field_value:

            if char.isdigit():
                continue

            if char not in allowed_specials:
                raise ValueError(f"Invalid special character {char} in field {field_value}. Allowed values are: {allowed_specials}.")
    
    def validate_all(self,field_name):
        """
        Validate '*' field and return all possible values for that field.
        """
        min_value = self.field_name_value_mapping[field_name]["range"][0]
        max_value = self.field_name_value_mapping[field_name]["range"][1]

        return list(range(min_value,max_value+1))


    def is_range(self,value):
        """
        Check if the value matches the range pattern.
        """
        return bool(self.range_pattern.match(value))
    
    def is_single_value_pattern(self,value):
        """
        Check if the value matches the single value pattern.
        """
        return bool(self.single_value_pattern.match(value))

    def is_range_increment_pattern(self,value):
        """
        Check if the value matches the range increment pattern.
        """
        return bool(self.range_increment_pattern.match(value))
    
    def validate_increments(self,field_name,field):
        """
        Validate increments (e.g., '*/5' or '1-10/2') and return the expanded values.
        """
        min_value = self.field_name_value_mapping[field_name]["range"][0]
        max_value = self.field_name_value_mapping[field_name]["range"][1]

        base, step = field.split('/')

        if base == "*":
            base = min_value

        elif self.is_range(base):

            min_range,max_range = list(map(int,base.split("-")))

            base =  min_range
            min_value = min_range

            if max_range < max_value:
                max_value = max_range

        base = int(base)
        step = int(step)

        if step <= 0:
            raise InvalidCronRangeError(field_name, field, "Increment step must be greater than zero")
        if base < min_value or base > max_value:
            raise InvalidCronRangeError(field_name, field, f"Base value {base} is out of range")


        return list(range(base, max_value+1, step))

    def validate_range(self,field_name,field):
        """
        Validate ranges (e.g., '1-5') and return the expanded values.
        """
        min_value = self.field_name_value_mapping[field_name]["range"][0]
        max_value = self.field_name_value_mapping[field_name]["range"][1]

        start, end = map(int, field.split('-'))

        if start < min_value or start > max_value or end < min_value or end > max_value:
            raise InvalidCronRangeError(field_name, field, "Values are out of range")
        

        if start > end:
            final_range = list(range(start,max_value+1)) + list(range(min_value,end+1))
            return sorted(final_range)


        return list(range(start, end + 1))


    def validate_multiple_commas(self, field_name, field):
        """
        Validate multiple values separated by commas (e.g., '1,2,3') and return the unique expanded values.
        """
        values = list(map(int, field.split(',')))
        min_value = self.field_name_value_mapping[field_name]["range"][0]
        max_value = self.field_name_value_mapping[field_name]["range"][1]

        for value in values:
            if value < min_value or value > max_value:
                raise InvalidCronRangeError(field_name, field, f"Value {value} is out of range")
        
        return sorted(set(values)) 

    def validate_single_value(self, field_name, field):
        """
        Validate a single value (e.g., '5') and return it in a list.
        """
        value = int(field)
        min_value = self.field_name_value_mapping[field_name]["range"][0]
        max_value = self.field_name_value_mapping[field_name]["range"][1]

        if value < min_value or value > max_value:
            raise InvalidCronRangeError(field_name, field, f"Value {value} is out of range")

        return [value]
    
    def validate_multiple_conditions(self,field_name, field):
        """
        Validate fields that contain multiple types of conditions (e.g., '1-10/2,20') and return the combined expanded values.
        """
        parts = field.split(',')

        values = []

        for part in parts:

            if self.is_range(part):

                values.extend(self.validate_range(field_name,part))
            
            elif self.is_range_increment_pattern(part):
                values.extend(self.validate_increments(field_name,part))
            
            elif self.is_single_value_pattern(part):
                values.extend(self.validate_single_value(field_name,part))
            
            elif part == "*":
                values.extend(self.validate_all(field_name))
        
        return sorted(set(values))
    
    def print_result(self, result_dict):
        """
        Print the results for each field in the cron dictionary.
        """
        for field_name in self.field_names:
            if field_name != "command":
                values = result_dict.get(field_name, [])
                print(f"{field_name.ljust(14)}{' '.join(map(str, values))}")
        print(f"command       {self.command}")

    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parser.py '<cron_expression>'")
    else:
        try:
            parser = Parser(sys.argv[1])
            result = parser.split_expression()
            parser.print_result(result)
        except (ValueError, InvalidCronRangeError) as e:
            print(e)







        