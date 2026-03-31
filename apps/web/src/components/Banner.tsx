import { useEffect } from 'react';

interface AdsenseProps{
    format: string
}

const AdSense = ({format}: AdsenseProps) => {
  useEffect(() => {
    try {
      ((window as any).adsbygoogle = (window as any).adsbygoogle || []).push({});
    } catch (e) {
      console.error(e);
    }
  }, []);

  return (
    <ins
      className="adsbygoogle"
      style={{ display: 'block' }}
      data-ad-client="ca-pub-1450769283178899"
      data-ad-slot="7986001189"
      data-ad-format={format}
      data-full-width-responsive="true"
    ></ins>
  );
};

export default AdSense;