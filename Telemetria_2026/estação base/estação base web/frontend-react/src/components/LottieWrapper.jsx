import React from 'react';
import LottieRaw from 'lottie-react';

const Lottie = LottieRaw?.default || LottieRaw;

export default function LottieWrapper(props) {
  if (typeof Lottie === 'function') {
    return <Lottie {...props} />;
  }
  return null;
}
