import { createChart, ColorType, LineSeries, Time, LineData, HistogramSeries, HistogramData } from 'lightweight-charts';
import { useEffect, useRef } from 'react';


export interface ChartProps {
    lineData: LineData<Time>[];
    histogramData: HistogramData<Time>[];
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
        lineData,
        histogramData,
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
                leftPriceScale: {
                    visible: true,
                },
                width: chartContainerRef.current.clientWidth,
                height: 300,
            });

            chart.timeScale().fitContent();

            if (lineData.length > 0){
                const newSeries = chart.addSeries(LineSeries, {
                    priceScaleId: 'right'
                });
                newSeries.setData(lineData);
            }

            if (histogramData.length > 0){
                const histogramSeries = chart.addSeries(HistogramSeries, { 
                    color: '#26a69a',                    
                    priceFormat: { type: 'volume' },
                    priceScaleId: 'left'
                 });

                histogramSeries.priceScale().applyOptions({
                    scaleMargins: {
                        top: 0.8, // Leave the top 80% of the chart space empty
                        bottom: 0,
                    },
                })

                histogramSeries.setData(histogramData);    
            }

            window.addEventListener('resize', handleResize);

            return () => {
                window.removeEventListener('resize', handleResize);

                chart.remove();
            };
        },
        [lineData, histogramData, backgroundColor, lineColor, textColor, gridColor]
    );

    return (
        <div
            ref={chartContainerRef}
        />
    );
};


