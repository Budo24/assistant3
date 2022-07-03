"""Read constants."""
ordinal_number_to_number = {'first': '01',
                            'second': '02',
                            'third': '03',
                            'fourth': '04',
                            'fifth': '05',
                            'sixth': '06',
                            'seventh': '07',
                            'eight': '08',
                            'ninth': '09',
                            'tenth': '10',
                            'eleventh': '11',
                            'twelfth': '12',
                            'thirteenth': '13',
                            'fourteenth': '14',
                            'fifteenth': '15',
                            'sixteenth': '16',
                            'seventeenth': '17',
                            'eighteenth': '18',
                            'nineteenth': '19',
                            'twentieth': '20',
                            'twenty first': '21',
                            'twenty second': '22',
                            'twenty third': '23',
                            'twenty fourth': '24',
                            'twenty fifth': '25',
                            'twenty sixth': '26',
                            'twenty seventh': '27',
                            'twenty eight': '28',
                            'twenty ninth': '29',
                            'thirty': '30',
                            'thirty first': '31',
                            }
days_ordinal_numbers_keywords = ['first', 'second', 'third',
                                 'fourth', 'fifth', 'sixth', 'seventh',
                                 'eighth', 'ninth', 'tenth', 'eleventh',
                                 'twelfth', 'thirteenth', 'fourteenth',
                                 'fifteenth', 'sixteenth', 'seventeenth',
                                 'eighteenth', 'nineteenth', 'twentieth',
                                 'twenty first', 'twenty second', 'twenty third',
                                 'twenty fourth', 'twenty fifth', 'twenty sixth',
                                 'twenty seventh', 'twenty eight', 'twenty ninth',
                                 'thirty', 'thirty first']


month_number_to_word = {'01': 'january',
                        '02': 'february',
                        '03': 'march',
                        '04': 'april',
                        '05': 'may',
                        '06': 'june',
                        '07': 'july',
                        '08': 'august',
                        '09': 'september',
                        '10': 'october',
                        '11': 'novemeber',
                        '12': 'december',
                        }


month_days = {'01': '31',
              '02': '28',
              '03': '31',
              '04': '30',
              '05': '31',
              '06': '30',
              '07': '31',
              '08': '31',
              '09': '30',
              '10': '31',
              '11': '30',
              '12': '31',
              }
hour_number_to_word = {'00': 'zero',
                       '01': 'one',
                       '02': 'two',
                       '03': 'three',
                       '04': 'four',
                       '05': 'five',
                       '06': 'six',
                       '07': 'seven',
                       '08': 'eight',
                       '09': 'nine',
                       '10': 'ten',
                       '11': 'eleven',
                       '12': 'twelve',
                       '13': 'thirteen',
                       '14': 'fourteen',
                       '15': 'fifteen',
                       '16': 'sixteen',
                       '17': 'seventeen',
                       '18': 'eighteen',
                       '19': 'nineteen',
                       '20': 'twenty',
                       '21': 'twenty one',
                       '22': 'twenty two',
                       '23': 'twenty three',
                       }

minute_number_to_word = {'30': 'thirty',
                         '00': 'zero',
                         }

actions_keywords = ['break',
                    'show',
                    'delete',
                    'activity',
                    'delete activity',
                    'insert',
                    ]

answers = ['I did not understand the date, can you please repeat, or say '
           'break,  if you do not want to insert,you can also say show dates,'
           ' but I understan it just in that form',

           'Which date do you want to insert, say me just ordinal number of day in date',

           'Which date do you want to delete',

           'On which date you want to add activity',

           'Ok insert of date is broken',

           'That date is in the past for this month, mothly plan provides just future',

           'if you want to plan, than plan for tomorrow,'
           ' monthly plan does not provides plannig in the same day for now',

           'Protocol broken',

           'Insert of date is broken',

           'Deleting of date broken',

           'Adding of activity broken',

           'Date exist in monthly plan, you can try to add time range of activity',
           ]
