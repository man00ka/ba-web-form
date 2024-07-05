# ba-online-form
This is the code base for the online form I used for my bachelor thesis to collect human written summarizations and simplifications which afterwerds where compared against AI generated summarizations/simplifications.

The app was written in python [flask](https://flask.palletsprojects.com/en/3.0.x/installation/#python-version), uses some basic html and css and was deployed via [vercel](https://vercel.com/home).

You can visit the online form [here](https://online-formular.vercel.app).


## Motivation
I was looking for a way to collect **human written summaries**. It needed to have a *low threshold for participation* and also be *easy to distribute*. A link to an online form with the texts to be summarized and a submission field for the summarization seemed ideal. However, none of the modular online form builders I have tried seemed to provide a way (at least not obvious to me) to realise a feature I realy wanted: Increasing the chance of a text to be displayed if it was less often summarized than the other texts, meaning a logic to negatively weigh the texts with respect to the number of summaries they each received.

So I wrote my own web-app for that.


## Requirements

### Dependencies

The form / web app depends on
- flask
- vercel
- numpy
- psycopg2-binary

Also a vercel account (free) and a postgres database was used, because the vercel runtime environment is readonly and for my idea to work read/write access was necessary.

Vercel also provides a way to **store environment variables** like e-mail adresses,  passworts, database access, etc. **in an encrypted form**. These information are necessary for the online forms workflow (using the database, transmitting submissions via e-mail, etc.).

### Export variables
Also an `export_vars.sh` bash script is expected if one wants to **examine the form locally** prior deploying via vercel. It needs to be run once per bash session prior to viewing the form. If you don't need that, you can skip this part.

The `export_vars.sh` can be beuilt from this draft:

```bash
export SMTP_SERVER= ...
export SMTP_PORT= ...
export SMTP_USERNAME= ...
export SMTP_PASSWORD= ...
export EMAIL_FROM= ...
export EMAIL_TO= ...
export APP_SECRET_KEY= ... 

export POSTGRES_URL= "postgres:// ..." # The URL to your postgres database
export POSTGRES_PORT= ...
export POSTGRES_HOST= ...
```

The SMTP and EMAIL statements are used to have simple way to receive submissions, i.e. just sending the summarized text from *me* (`EMAIL_FROM`) to *me* (`EMAIL_TO`) upon clicking the *submit* button in the form.
