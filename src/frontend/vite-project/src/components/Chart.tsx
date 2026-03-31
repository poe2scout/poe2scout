import { createChart, ColorType, Time, LineData, HistogramData, UTCTimestamp, IChartApi, ISeriesApi, HistogramSeries, LineSeries } from 'lightweight-charts';
import { useEffect, useRef } from 'react';
import { LegendData } from './ItemHistoryChartLegend';

export interface ChartData {
    lineData: LineData<Time>[];
    histogramData: HistogramData<Time>[];
}

export interface ChartProps {
    chartData: ChartData
    colors?: {
        backgroundColor?: string;
        lineColor?: string;
        textColor?: string;
        gridColor?: string;
    };
    onLoadMore: () => void;
    hasMore: boolean;
    isLoadingMore: boolean;
    onLegendDataChange: (data: LegendData) => void;
    height: number;
}


export const Chart = (props: ChartProps) => {
    const {
        chartData,
        colors: {
            backgroundColor = 'rgba(255, 255, 255, 0.0)',
            lineColor = '#2962FF',
            textColor = 'white',
            gridColor = '#334158',
        } = {},
        onLoadMore,
        hasMore,
        isLoadingMore,
        onLegendDataChange,
        height
    } = props;

    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const seriesRef = useRef<{ line: ISeriesApi<"Line"> | null; histo: ISeriesApi<"Histogram"> | null }>({ line: null, histo: null });
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
            height: height,
            timeScale: { borderVisible: false }
        });

        chart.priceScale('right').applyOptions({ scaleMargins: { top: 0.1, bottom: 0.1 } });

        const lineSeries = chart.addSeries(LineSeries, { priceScaleId: 'right', color: lineColor });
        lineSeries.priceScale().applyOptions({ scaleMargins: { top: 0.15, bottom: 0.15 } });

        const histogramSeries = chart.addSeries(HistogramSeries, { color: '#26a69a', priceFormat: { type: 'volume' }, priceScaleId: 'left' }, 1);

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
                const lastPrice = chartData.lineData[chartData.lineData.length - 1];
                const lastVolume = chartData.histogramData[chartData.histogramData.length - 1];
                onLegendDataChange({ price: lastPrice?.value, volume: lastVolume?.value, time: lastVolume?.time as UTCTimestamp });
                return;
            }
            const volumeData = data.get(histogramSeries) as HistogramData<Time>;
            const priceData = data.get(lineSeries) as LineData<Time>;
            onLegendDataChange({ price: priceData.value, volume: volumeData.value, time: volumeData.time as UTCTimestamp });
        };

        chart.subscribeCrosshairMove(handleCrosshairMove);

        return () => chart.unsubscribeCrosshairMove(handleCrosshairMove);
    }, [chartData, onLegendDataChange]);

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
            seriesRef.current.line.setData(chartData.lineData);
        }
        if (seriesRef.current.histo) {
            seriesRef.current.histo.setData(chartData.histogramData);
        }

        if (chartData.lineData.length > 0 && chartData.lineData.length <= 100) {
            chartRef.current?.timeScale().fitContent();
        }

        const lastPrice = chartData.lineData[chartData.lineData.length - 1];
        const lastVolume = chartData.histogramData[chartData.histogramData.length - 1];
        onLegendDataChange({ price: lastPrice?.value, volume: lastVolume?.value, time: lastVolume?.time as UTCTimestamp });
    }, [chartData, onLegendDataChange]);

    return (
        <>
            {isLoadingMore && <div style={{ position: 'absolute', top: '50%', left: '20px', zIndex: 20, color: 'white' }}>Loading...</div>}
            <div ref={chartContainerRef} />
        </>
    );
};