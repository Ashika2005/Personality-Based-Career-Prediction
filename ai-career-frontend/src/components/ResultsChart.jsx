import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function ResultsChart({ scores }) {
  const labels = Object.keys(scores);
  const dataPoints = Object.values(scores);
  
  const data = {
    labels: labels,
    datasets: [
      {
        label: 'Compatibility Score',
        data: dataPoints,
        backgroundColor: 'rgba(0, 123, 255, 0.6)',
        borderColor: 'rgba(0, 123, 255, 1)',
        borderWidth: 1,
      },
    ],
  };
  
  const options = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Your Top 10 Career Matches',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `Compatibility: ${(context.parsed.x * 100).toFixed(1)}%`;
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        max: 1.0,
        ticks: {
          callback: function(value) {
            return (value * 100) + '%';
          }
        }
      },
    },
  };

  return <Bar data={data} options={options} />;
}
export default ResultsChart;