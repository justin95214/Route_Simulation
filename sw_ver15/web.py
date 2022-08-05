import argparse
from dash import Dash, dcc, html
import dash

parser = argparse.ArgumentParser()

parser.add_argument('--location', required=True)
parser.add_argument('--num', required=True)

args = parser.parse_args()
app = Dash(__name__)

app.layout = html.Div([
html.H1(args.location+" -- "+args.num),
html.Iframe(id= 'table1',srcDoc=open(f'./map_test/'+args.location+'/월Mapped_Route'+args.num+'_route.html', 
encoding='euc-kr').read(), width='100%', height='100'),
html.Iframe(id= 'map', srcDoc=open(f'./map_test/'+args.location+'/월_Mapped_Route'+args.num+'_map_test.html').read(), 
width='100%', height='600'), 
html.Iframe(id= 'table2',srcDoc=open(f'./map_test/'+args.location+'/월Mapped_Route'+args.num+'_detail.html', 
encoding='euc-kr').read(), width='100%', height='100%')
	 ])
	


if __name__ == '__main__':
	app.run_server(debug=True)
