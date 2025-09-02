import { createChart, ColorType, LineSeries, Time, LineData, HistogramSeries, HistogramData, UTCTimestamp } from 'lightweight-charts';
import { useEffect, useRef, useState } from 'react';
import { fromUnixTime, format } from "date-fns";

export interface ChartProps {
    lineData: LineData<Time>[];
    histogramData: HistogramData<Time>[];
    colors?: {
        backgroundColor?: string;
        lineColor?: string;
        textColor?: string;
        gridColor?: string;
    };
}

interface LegendData {
    price?: number;
    volume?: number;
    time?: UTCTimestamp;
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

    const lastPrice = lineData[lineData.length - 1];
    const lastVolume = histogramData[histogramData.length - 1];
    const [legendValues, setLegendValues] = useState<LegendData>({
        price: lastPrice?.value, 
        volume: lastVolume?.value, 
        time: lastVolume?.time as UTCTimestamp
    });

    useEffect(() => {
        if (!chartContainerRef.current || lineData.length === 0 || histogramData.length === 0) {
            return;
        }

        const handleResize = () => {
            chart.applyOptions({ width: chartContainerRef.current!.clientWidth });
        };

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: backgroundColor },
                textColor,
            },
            rightPriceScale: {
                borderVisible: false,
            },
            leftPriceScale: {
                visible: true,
                borderVisible: false,
            },
            grid: {
                vertLines: { color: gridColor },
                horzLines: { color: gridColor },
            },
            width: chartContainerRef.current.clientWidth,
            height: 500,
            timeScale: {
                borderVisible: false,
            }
        });

        chart.priceScale('right').applyOptions({
            scaleMargins: {
                top: 0.1,
                bottom: 0.1,
            },
        });

        const lineSeries = chart.addSeries(LineSeries, {
            priceScaleId: 'right',
            color: lineColor,
        });

        lineSeries.priceScale().applyOptions({
            scaleMargins: {
                top: 0.15,
                bottom: 0.15
            }
        })
        lineSeries.setData(lineData);

        const histogramSeries = chart.addSeries(HistogramSeries, {
            color: '#26a69a',
            priceFormat: { type: 'volume' },
            priceScaleId: 'left',
        });

        histogramSeries.priceScale().applyOptions({
            scaleMargins: {
                top: 0.75, 
                bottom: 0,
            },
        });
        
        histogramSeries.setData(histogramData);

        chart.subscribeCrosshairMove(param => {
            if (!param.time || !param.seriesData.has(histogramSeries) || !param.seriesData.has(lineSeries)) {
                 setLegendValues({
                    price: lastPrice?.value,
                    volume: lastVolume?.value,
                    time: lastVolume?.time as UTCTimestamp
                 });
                return;
            }

            const volumeData = param.seriesData.get(histogramSeries) as HistogramData<Time>;
            const priceData = param.seriesData.get(lineSeries) as LineData<Time>;

            setLegendValues({
                price: priceData.value,
                volume: volumeData.value,
                time: volumeData.time as UTCTimestamp
            });
        });

        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [lineData, histogramData, backgroundColor, lineColor, textColor, gridColor]);

    return (
        <div style={{ position: 'relative', width: '100%' }}>
            <div
                style={{
                    position: 'absolute',
                    top: 12,
                    left: 75,
                    zIndex: 10,
                    color: textColor,
                    fontFamily: 'sans-serif',
                    fontSize: '14px',
                    pointerEvents: 'none',
                }}
            >
                {legendValues.price !== undefined && (
                    <div>
                        <span style={{ color: '#aaa' }}>Price: </span>
                        <strong style={{ color: 'white' }}>
                            {legendValues.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </strong>
                        <span style={{ color: '#aaa' }}> Exalted Orbs</span>
                    </div>
                )}
                {legendValues.volume !== undefined && (
                    <div>
                        <span style={{ color: '#aaa' }}>Volume: </span>
                        <strong style={{ color: 'white' }}>{legendValues.volume.toLocaleString()}</strong>
                    </div>
                )}
                {legendValues.time !== undefined && (
                    <div style={{ color: '#aaa', marginTop: '4px' }}>
                        {format(fromUnixTime(legendValues.time as number), "dd MMM yyyy, HH:mm")}
                    </div>
                )}
            </div>
            <div ref={chartContainerRef} />
        </div>
    );
};