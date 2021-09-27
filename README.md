# Travel Day Counter - Traveler's Statistics

## Intro
* **Travel Day Counter** is a toolkit that helps track all your visited countries and provides an overview of how long you spent in each one, when you last vivsited them, and much more.
* A list of all features can be found under the `Features` section.

## Dependencies
* `pandas`

## Quick Start
* To quickly try it out with sample data, simply run `python TDC.py`.
* The output consists of a header and three customizable sections
```
# EXAMPLE OUTPUT

Travel Day Counter
** countries visited until ****-**-**

Inside **: ** days (** years, **%)
Outside **: ** days (** years, **%)
Residency in **: ** year(s) ** day(s)

COUNTRY     DAYS	%	    RANK.	FIRST VISIT	    LAST VISIT
XX          **	    **%     **	    ****-**-**	    ****-**-**
YY          **	    **%	    **  	****-**-**	    ****-**-**
OTHER	    **	    **%

Chronological Report
[2000] XX
[2010] XX YY
[2015] YY ZZ
[2016] ZZ YY
[2020] YY XX
[2021] XX
```

## Set-up Guide
* **Set-up for your own travel history**
    * You should modify `travel_history.csv`, or create a new one.
    * In each line, enter a date (yyyy-mm-dd) and a country code following the given syntax, be consistent with the system used (e.g. [ISO 3166-1](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)).
    * Ideally, you should put your date and country of birth in the first line.
    ```
    DATE,ENTERED
    2000-01-01,XX
    ```
* **Configuring the output**
    * The output sections can be customized by modifying `config.json`.
    * `source` - this should a `csv` file, you can create one with a name of your choice
    * `lang` - swap in the language code to change the language, currently supported are **English** (`en`), **Korean** (`ko`), **traditional Chinese** (`zh`)
    * `track_home` - (`true`/`false`) activate it if you wish to compare the time spent home and abroad
    * `home_code` - your home country's country code, use the same system as in your `source` data
    * `home_name` - this is how the country's name is displayed in natural language
    * `track_residency` - (`true`/`false`) if you live abroad, you can track how long you have lived in your country of residence
    * `residency_code`, `residency_name` - ref. `home_code` and `home_name`
    * `residency_begin` - ("yyyy-mm-dd") the starting date of your residency
    * `table_style` - (`short`/`full`) viewing option for the main table of statistics, if `short` is chosen, only countries with stays longer than a threshold (7 days by default) are displayed as separate entries, all other countries are grouped together
    * `report_style` - the only option supported currently is `chrono`, which prints visited countries sorted by year, the report can be disabled by setting the value to `null`
    ```
    {
    "source": "travel_history.csv",
    "lang": "en",
    "track_home": true,
    "home_code": "XX",
    "home_name": "Gallifrey",
    "track_residency": true,
    "residency_code": "YY",
    "residency_name": "Earth",
    "residency_begin": "2010-01-01",
    "table_style": "short",
    "report_style": "chrono"
    }
    ```

## Features
* **Travel history & statistics**
* **Track days home & abroad**
* **Track residency**
* **Generate a report**