#!/usr/bin/env python
import configargparse
from get_result import get_result
from collect_result import collect_result

def call_get_result(args):
	arglist = ['dbpath','degree','session','year','request_chunk_size','database_chunk_size','pool_size']
	get_result(**{ k:getattr(args,k) for k in arglist })

def call_collect_result(args):
	arglist = ['dbpath','degree','session','year','chunk_size']
	collect_result(**{k:getattr(args,k) for k in arglist})

parser = configargparse.Parser()
parser.add('-l','--log-dir',help='The directory to put log files in.')

subparsers= parser.add_subparsers()

parser_get = subparsers.add_parser('get',help='This command fetches the data from the net.')
parser_get.add('-c','--conf-file',is_config_file=True)
parser_get.add('--degree',required=True)
parser_get.add('--session',required=True)
parser_get.add('--year',required=True,type=int)
parser_get.add('--request-chunk-size',type=int,default=1000)
parser_get.add('--database-chunk-size',type=int,default=100)
parser_get.add('--pool-size',type=int,default=100)
parser_get.add('--dbpath',required=True)
parser_get.set_defaults(func=call_get_result)

parser_collect = subparsers.add_parser('collect',help='This command fetches the data from the net.')
parser_collect.add('-c','--conf-file',is_config_file=True)
parser_collect.add('--dbpath',required=True)
parser_collect.add('--degree',required=True)
parser_collect.add('--session',required=True)
parser_collect.add('--year',required=True,type=int)
parser_collect.add('-j','--chunk-size',type=int,default=100)
parser_collect.set_defaults(func=call_collect_result)

args = parser.parse_args()
args.func(args)
