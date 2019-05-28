class MissingValue:    
    def __str__(self):
        return "MISSING"
    
class OptionalValue:    
    def __str__(self):
        return "OPTIONAL"

MISSING_VALUE  = MissingValue()
OPTIONAL_VALUE = OptionalValue()