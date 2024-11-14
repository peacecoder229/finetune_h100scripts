def is_palindrome(s):
    return s == s[::-1]

def to_binary(n):
    return bin(n)[2:]

def is_double_palindrome(n):
    # Convert to string for base 10 palindrome check
    n_str = str(n)
    
    # Convert to binary string for base 2 palindrome check
    n_bin = to_binary(n)
    
    # Check if both are palindromes
    return is_palindrome(n_str) and is_palindrome(n_bin)

# Example usage
number = 585  # 585 is 1001001001 in binary, both are palindromes
result = is_double_palindrome(number)
print(f"Is {number} a double palindrome? {result}")

