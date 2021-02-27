import parse

# columns={0:"date", 1:"code",2:"target",3:"time",4:"price",5:"volumn"}
# df.rename, df.loc[df[column]==name],df.groupby

if __name__ == '__main__':
    classes = (parse.MTX, parse.Stock)
    for c in classes:
        obj = c()
        obj.run()
