//d3 template to generate a radial tree diagram
//see original at http://mbostock.github.com/d3/ex/tree.html

var generate_tree = function(){
	var radius = 960 / 2;
	
	var tree = d3.layout.tree()
	    .size([360, radius - 120])
	    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });
	
	var diagonal = d3.svg.diagonal.radial()
	    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });
	
	//clear chart before re-drawing for new submits
	document.getElementById("chart").innerHTML = "";

	var vis = d3.select("#chart").append("svg")
	    .attr("width", radius * 2 + 150)
	    .attr("height", radius * 2 + 200)
	  .append("g")
	    .attr("transform", "translate(" + (radius + 50) + "," + (radius + 100) + ")");
	
	//grab input name
	var name = document.getElementById('name').value

	d3.json('/' + name, function(json) {
	  var nodes = tree.nodes(json);
	
	  var link = vis.selectAll("path.link")
	      .data(tree.links(nodes))
	    .enter().append("path")
	      .attr("class", "link")
	      .attr("d", diagonal);
	
	  var node = vis.selectAll("g.node")
	      .data(nodes)
	    .enter().append("g")
	      .attr("class", "node")
	      .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })
	      .attr('id', function(d) {
	      	if (d.parent){
	      		return d.name + '-'+ d.parent.name
	      	}
	      	else {
	      		return d.name
	      	}

	      	})
	      .attr('title', function(d){return d.depth})

	  node.append("circle")
	      .attr("r", 4.5);
	
	  node.append("text")
	      .attr("dy", ".31em")
	      .attr("class", "text")
	      .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
	      .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
	      .text(function(d) { return d.name; });

	   	$('.node').click(function(e) {
	   		var name = $.trim($(this).attr('id').split('-')[0].split('(')[0])
			var parent = $(this).attr('id').split('-')[1]
			var closed = null;
			//if something's already open
			if ($('.tooltip').length > 0) {
				closed = $('.tooltip').remove()
			}
			//if it doesn't belong to just clicked thing
			if ((!closed) || (closed.attr('id') !== name + '-' + parent)){
				var depth = $(this).attr('title')
				var x = e.pageX
				var y = e.pageY-100
				if (depth == 2){
					$.get('/' + name + '/' + parent, function(data){
						var lines = $.parseJSON(data)
						var currDisp = 0
						d3.select('#chart').append('div')
							.style('top', y + 'px')
							.style('left', x + 'px')
							.attr('class', 'tooltip')
							.attr('id', name + '-' + parent)
							.html("<span class='close'>x</span> <p id='snip'>" + lines[currDisp]+ "</p><div><span id ='prev'>Previous</span> <span id='next'>Next</span></div>")

						$('.close').click(function(){
							$(this).parent().remove()
						})

						$('#next').click(function() {
							currDisp = Math.min(currDisp+1, lines.length-1)
							$('#snip').text(lines[currDisp][0])
						})

						$('#prev').click(function() {
							currDisp = Math.max(currDisp-1, 0)
							$('#snip').text(lines[currDisp][0])
						})
					});
				}
			}
		})
	});
};


$(document).ready(function(){
	$('#form').submit(function(){
		generate_tree();
		return false;
	});
	$('#name').focus()
});