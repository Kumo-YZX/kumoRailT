def test(actArrId):
    import actArr
    obj = actArr.table()
    from datetime import date
    theDate = date(2010,10,1)
    obj.new(actArrId, theDate)

if __name__ == "__main__":
    import sys
    ar = int(sys.argv[1])
    test(ar)