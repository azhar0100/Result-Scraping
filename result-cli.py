#!/usr/bin/env python
import configargparse
from get_result import get_result

def call_get_result(args):
	arglist = ['dbpath','degree','session','year','request_chunk_size','database_chunk_size','pool_size']
	get_result(**{ k:getattr(args,k) for k in arglist })

parser = configargparse.Parser()
parser.add('-l','--log-dir',help='The directory to put log files in.')

subparsers= parser.add_subparsers()

parser_get = subparsers.add_parser('get',help='This command fetches the data from the net.')
parser_get.add('-c','--conf-file',required=True,is_config_file=True)
parser_get.add('--degree',required=True)
parser_get.add('--session',required=True)
parser_get.add('--year',required=True,type=int)
parser_get.add('--request-chunk-size',type=int,default=1000)
parser_get.add('--database-chunk-size',type=int,default=100)
parser_get.add('--pool-size',type=int,default=100)
parser_get.add('--dbpath',required=True)
parser_get.set_defaults(func=call_get_result)

args = parser.parse_args()
args.func(args)
