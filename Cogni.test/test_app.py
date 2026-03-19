import app

print('import success')

with app.app.test_request_context('/', method='POST', data={'difficulty':'Easy','wpm':'30','errors':'2','backspaces':'5','pauses':'1','accuracy':'92'}):
    r = app.submit()
    print('submit status', r.status)

with app.app.app_context():
    try:
        out = app.result(1)
        print('result returned', type(out))
    except Exception as e:
        print('result error', e)
    try:
        ai = app.ai_analysis(1)
        print('ai returned', type(ai))
    except Exception as e:
        print('ai error', e)
