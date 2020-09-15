function renderChart(data, expected_data, labels) {
    var ctx = document.getElementById("myChart").getContext('2d');
    console.log(ctx, data, labels)
    var myChart = new Chart(ctx, {
        type: 'bar',
        options: {
            title: {
                display: true,
                text: "Found vs. Expected"
                },
            scales: {
                 yAxes: [{
                     ticks: {
                        callback: function (value) {
                          return (value * 100).toFixed(0) + '%'; // convert to percentage
                        },
                     },
                      scaleLabel: {
                        display: true,
                        labelString: 'Percentage',
                      },
                    },
                  ],
                },
              },
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Found",
                    data: data,
                    backgroundColor: "rgb(135,206,250)",
                    borderColor: "rgb(135,206,250)",
                },
                {
                    label: "Expected",
                    data: expected_data,
                    borderColor: "rgb(205,92,92)",
                    pointBackgroundColor: "rgb(255,165,0)",
                    type: "line"
                },
            ]
        },
    });
}
function ProcessFile() {

  var form_data = new FormData();
  form_data.append('file', $('#File')[0].files[0]);
  $.ajax({
    type: 'POST',
    url: '/',
    data: form_data,
    processData: false,
    contentType: false,
    success: function (data) {
        renderChart(data.found_values, data.expected_values, data.labels);
    },
    error: function(data) {
        alert(data.responseJSON.idf);
    },
  });
}
