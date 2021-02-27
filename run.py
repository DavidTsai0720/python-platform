import parse

if __name__ == '__main__':
    classes = (parse.MTX, parse.Stock)
    for c in classes:
        obj = c()
        obj.run()
