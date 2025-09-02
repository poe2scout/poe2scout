import { createChart, ColorType, LineSeries, Time, LineData } from 'lightweight-charts';
import { useEffect, useRef } from 'react';


export interface ChartProps {
    data: LineData<Time>[];
    colors?: {
        backgroundColor?: string;
        lineColor?: string;
        textColor?: string;
        areaTopColor?: string;
        areaBottomColor?: string;
        gridColor?: string; 
    };
}

export const Chart = (props: ChartProps) => {
    const {
        data,
        colors: {
            backgroundColor = 'rgba(255, 255, 255, 0.0)',
            lineColor = '#2962FF',
            textColor = 'white',
            gridColor = '#334158', 
        } = {},
    } = props;

    const chartContainerRef = useRef<HTMLDivElement>(null);

    useEffect(
        () => {
            if (!chartContainerRef.current) {
                return;
            }
            const handleResize = () => {
                if (!chartContainerRef.current) {
                    return;
                }
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            };

            const chart = createChart(chartContainerRef.current, {
                layout: {
                    background: { type: ColorType.Solid, color: backgroundColor },
                    textColor,
                },
                width: chartContainerRef.current.clientWidth,
                height: 300,
            });
            chart.timeScale().fitContent();

            const newSeries = chart.addSeries(LineSeries);
            newSeries.setData(data);

            window.addEventListener('resize', handleResize);

            return () => {
                window.removeEventListener('resize', handleResize);

                chart.remove();
            };
        },
        [data, backgroundColor, lineColor, textColor, gridColor]
    );

    return (
        <div
            ref={chartContainerRef}
        />
    );
};


