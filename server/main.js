(function(d3) {

  var svg = d3.select("body").append("svg")
        .attr("width", 1920)
        .attr("height", 700),
      margin = {top: 20, right: 20, bottom: 30, left: 50},
      width = +svg.attr("width") - margin.left - margin.right,
      height = +svg.attr("height") - margin.top - margin.bottom,
      g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var parseTime = d3.timeParse("%d-%b-%y");

  var zoom = d3.zoom()
      //.scaleExtent([1 / 4, 8])
      .scaleExtent([1 / 4, Infinity])
      .translateExtent([[-width, -Infinity], [2 * width, Infinity]])
      .on("zoom", zoomed);

  var zoomRect = svg.append("rect")
      .attr("width", width)
      .attr("height", height)
      .attr("fill", "none")
      .attr("pointer-events", "all")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .call(zoom);


  var x = d3.scaleTime()
      .rangeRound([0, width]);

  var y = d3.scaleLinear()
      .rangeRound([height, 0]);

  var xGroup = g.append("g")
      .attr("transform", "translate(0," + height + ")");

  var xAxis = d3.axisBottom(x);
  xGroup.call(xAxis);

  var line = d3.line()
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y(d.temperature_celsius); });

  var lines;


  d3.json("readings", function(data) {


    var minDate;
    var maxDate;
    data.forEach(function(sensor) {
      sensor.readings.forEach(function(reading) {
        reading.date = new Date(reading.datetime + "-07:00");

        if (!minDate || reading.date < minDate) {
          minDate = reading.date;
        }
        if (!maxDate || reading.date > maxDate) {
          maxDate = reading.date;
        }

      });
    });

    console.log(minDate);
    console.log(maxDate);

    //data = data[0].readings;
    //data = data.slice(0, 1);

    //x.domain(d3.extent(data, function(d) { return d.date; }));
    x.domain([minDate, maxDate]);
    //y.domain(d3.extent(data, function(d) { return d.temperature_celsius; }));
    y.domain([20, 40]);

    g.append("g")
        .call(d3.axisLeft(y))
      .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .text("Price ($)");

    lines = g.append("g")
        .attr("class", "lines")
      .selectAll(".line")
        .data(data)
      .enter().append("path")
        .attr("class", "line")
    //g.append("path")
    //    .datum(data)
        .datum(function(d) {
          return d.readings;
        })
        .attr("fill", "none")
        .attr("stroke", function(d, i) {
          return d3.schemeCategory10[i];
        })
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .attr("stroke-width", 1.5)
        .attr("d", line);
  });

  function zoomed() {
    var xz = d3.event.transform.rescaleX(x);
    xGroup.call(xAxis.scale(xz));
    //areaPath.attr("d", area.x(function(d) { return xz(d.date); }));
    lines.attr("d", line.x(function(d) {
      return xz(d.date);
    }));
  }

}(d3));
