import { LegendData } from '../ItemHistoryChartLegend';
import { FormatTimeFromEpoch } from '../FormatTime';

export const SnapshotHistoryChartLegend = (props: LegendData) => {
    const {
        price,
        volume,
        time,
    } = props;

    if (price === undefined && volume === undefined && time === undefined) {
        return null;
    }

    if (window.innerWidth < 500) {
        return null;
    }

    return (
        <div style={{ position: 'absolute', top: 5, left: 10, zIndex: 10, fontFamily: 'sans-serif', fontSize: '14px', pointerEvents: 'none' }}>
            {price !== undefined && (
                <div>
                    <span style={{ color: '#aaa' }}>Market cap: </span>
                    <strong style={{ color: 'white' }}>{price.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })} ex</strong>
                </div>
            )}
            {volume !== undefined && (
                <div>
                    <span style={{ color: '#aaa' }}>Trading volume: </span>
                    <strong style={{ color: 'white' }}>{volume.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })} ex</strong>
                </div>
            )}
            {time !== undefined && (
                <div style={{ color: '#aaa', marginTop: '4px' }}>
                    {FormatTimeFromEpoch(time as number)}
                </div>
            )}
        </div>
    );
};