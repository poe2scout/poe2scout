import { format, fromUnixTime } from 'date-fns';
import { LegendData } from '../ItemHistoryChartLegend';

export const SnapshotHistoryChartLegend = (props: LegendData) => {
    const {
        price,
        volume,
        time,
    } = props;

    if (price === undefined && volume === undefined && time === undefined) {
        return null;
    }

    return (
        <div style={{ position: 'absolute', top: 12, left: 75, zIndex: 10, fontFamily: 'sans-serif', fontSize: '14px', pointerEvents: 'none' }}>
            {price !== undefined && (
                <div>
                    <span style={{ color: '#aaa' }}>Trading volume: </span>
                    <strong style={{ color: 'white' }}>{price.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })} ex</strong>
                </div>
            )}
            {volume !== undefined && (
                <div>
                    <span style={{ color: '#aaa' }}>Market cap: </span>
                    <strong style={{ color: 'white' }}>{volume.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })} ex</strong>
                </div>
            )}
            {time !== undefined && (
                <div style={{ color: '#aaa', marginTop: '4px' }}>
                    {format(fromUnixTime(time as number), "dd MMM yyyy, HH:mm")}
                </div>
            )}
        </div>
    );
};