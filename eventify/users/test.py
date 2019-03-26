def check_valid_card_test(card, sec, month, year, amount):
    if len(card) != 16 or not card.isdigit():
        print(f'Invalid card number. ')
        return False
    if len(sec) != 3 or not sec.isdigit():
        print(f'Invalid security code, should be three digits. ')
        return False
    if len(month) > 2 or not month.isdigit() or 0 >= int(month) >= 13:
        print(f'Invalid month, should be on the form mm where the value is between 1 and 12.')
        return False
    if len(year) != 2 or not year.isdigit() or int(year) < 19:
        print(f'Invalid year, should be on the form yy where the value is greater than the current year.')
        return False
    if int(amount) < 0:
        print(f'Invalid amount, must be a positive amount. ')
        return False
    print('Input good')
    return True

check_valid_card_test('1234123412341234', '123', '3', '20', 2)