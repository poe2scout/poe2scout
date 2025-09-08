import { createChart, ColorType, Time, LineData, HistogramData, UTCTimestamp, IChartApi, ISeriesApi, HistogramSeries, LineSeries } from 'lightweight-charts';
import { useEffect, useRef, useState } from 'react';
import { fromUnixTime, format } from "date-fns";
import { BaseCurrencies } from './ReferenceCurrencySelector';

export interface ChartProps {
    lineData: LineData<Time>[];
    histogramData: HistogramData<Time>[];
    colors?: {
        backgroundColor?: string;
        lineColor?: string;
        textColor?: string;
        gridColor?: string;
    };
    selectedReference: BaseCurrencies;
    onLoadMore: () => void;
    hasMore: boolean;
    isLoadingMore: boolean;
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
        selectedReference,
        onLoadMore,
        hasMore,
        isLoadingMore
    } = props;

    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const seriesRef = useRef<{ line: ISeriesApi<"Line"> | null; histo: ISeriesApi<"Histogram"> | null }>({ line: null, histo: null });
    const [legendValues, setLegendValues] = useState<LegendData>({});
    const loadingRef = useRef(false);
    const justLoadedRef = useRef(false);

    useEffect(() => {
        loadingRef.current = isLoadingMore;
    }, [isLoadingMore]);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        const chart = createChart(chartContainerRef.current, {
            layout: { background: { type: ColorType.Solid, color: backgroundColor }, textColor },
            rightPriceScale: { borderVisible: false },
            leftPriceScale: { visible: true, borderVisible: false },
            grid: { vertLines: { color: gridColor }, horzLines: { color: gridColor } },
            width: chartContainerRef.current.clientWidth,
            height: 500,
            timeScale: { borderVisible: false }
        });

        chart.priceScale('right').applyOptions({ scaleMargins: { top: 0.1, bottom: 0.1 } });

        const lineSeries = chart.addSeries(LineSeries, { priceScaleId: 'right', color: lineColor });
        lineSeries.priceScale().applyOptions({ scaleMargins: { top: 0.15, bottom: 0.15 } });

        const histogramSeries = chart.addSeries(HistogramSeries, { color: '#26a69a', priceFormat: { type: 'volume' }, priceScaleId: 'left' });
        histogramSeries.priceScale().applyOptions({ scaleMargins: { top: 0.75, bottom: 0 } });

        chartRef.current = chart;
        seriesRef.current = { line: lineSeries, histo: histogramSeries };

        const handleResize = () => chart.applyOptions({ width: chartContainerRef.current!.clientWidth });
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
            chartRef.current = null;
        };
    }, []);

    useEffect(() => {
        const chart = chartRef.current;
        const lineSeries = seriesRef.current.line;
        const histogramSeries = seriesRef.current.histo;
        if (!chart || !lineSeries || !histogramSeries) return;

        const handleCrosshairMove = (param: any) => {
            const data = param.seriesData;
            if (!param.time || !data.has(lineSeries) || !data.has(histogramSeries)) {
                const lastPrice = lineData[lineData.length - 1];
                const lastVolume = histogramData[histogramData.length - 1];
                setLegendValues({ price: lastPrice?.value, volume: lastVolume?.value, time: lastVolume?.time as UTCTimestamp });
                return;
            }
            const volumeData = data.get(histogramSeries) as HistogramData<Time>;
            const priceData = data.get(lineSeries) as LineData<Time>;
            setLegendValues({ price: priceData.value, volume: volumeData.value, time: volumeData.time as UTCTimestamp });
        };

        chart.subscribeCrosshairMove(handleCrosshairMove);

        return () => chart.unsubscribeCrosshairMove(handleCrosshairMove);
    }, [lineData, histogramData]);

    useEffect(() => {
        const chart = chartRef.current;
        if (!chart) return;

        const handleTimeRangeChange = () => {
            if (justLoadedRef.current) {
                justLoadedRef.current = false;
                return;
            }
            if (loadingRef.current || !hasMore) return;
            const logicalRange = chart.timeScale().getVisibleLogicalRange();

            if (logicalRange !== null && logicalRange.from < 10) {
                loadingRef.current = true;
                onLoadMore();
            }
        };

        chart.timeScale().subscribeVisibleTimeRangeChange(handleTimeRangeChange);

        return () => {
            chart.timeScale().unsubscribeVisibleTimeRangeChange(handleTimeRangeChange);
        };
    }, [onLoadMore, hasMore]);

    useEffect(() => {
        justLoadedRef.current = true;

        if (seriesRef.current.line) {
            seriesRef.current.line.setData(lineData);
        }
        if (seriesRef.current.histo) {
            seriesRef.current.histo.setData(histogramData);
        }

        if (lineData.length > 0 && lineData.length <= 100) {
            chartRef.current?.timeScale().fitContent();
        }

        const lastPrice = lineData[lineData.length - 1];
        const lastVolume = histogramData[histogramData.length - 1];
        setLegendValues({ price: lastPrice?.value, volume: lastVolume?.value, time: lastVolume?.time as UTCTimestamp });
    }, [lineData, histogramData]);

    return (
        <div style={{ position: 'relative', width: '100%' }}>
            <div style={{ position: 'absolute', top: 12, left: 75, zIndex: 10, color: textColor, fontFamily: 'sans-serif', fontSize: '14px', pointerEvents: 'none' }}>
                {legendValues.price !== undefined && (
                    <div><span style={{ color: '#aaa' }}>Price: </span><strong style={{ color: 'white' }}>{legendValues.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong><span style={{ color: '#aaa' }}> {selectedReference.charAt(0).toUpperCase() + selectedReference.slice(1)} Orbs</span></div>
                )}
                {legendValues.volume !== undefined && (
                    <div><span style={{ color: '#aaa' }}>Volume: </span><strong style={{ color: 'white' }}>{legendValues.volume.toLocaleString()}</strong></div>
                )}
                {legendValues.time !== undefined && (
                    <div style={{ color: '#aaa', marginTop: '4px' }}>{format(fromUnixTime(legendValues.time as number), "dd MMM yyyy, HH:mm")}</div>
                )}
            </div>
            {isLoadingMore && <div style={{ position: 'absolute', top: '50%', left: '20px', zIndex: 20, color: 'white' }}>Loading...</div>}
            <div ref={chartContainerRef} />
        </div>
    );
};