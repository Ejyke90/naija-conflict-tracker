import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const ConflictChart = ({ data }) => {
  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray='3 3' />
      <XAxis dataKey='date' />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type='monotone' dataKey='incidents' stroke='#8884d8' />
    </LineChart>
  );
};

export default ConflictChart;
