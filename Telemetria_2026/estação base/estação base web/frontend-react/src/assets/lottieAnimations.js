// Animações Lottie leves em formato JSON para o sistema de telemetria

export const radarPulseLottie = {
  v: "5.7.4",
  fr: 30,
  ip: 0,
  op: 60,
  w: 60,
  h: 60,
  nm: "Radar Pulse",
  ddd: 0,
  assets: [],
  layers: [
    {
      ddd: 0,
      ind: 1,
      ty: 4,
      nm: "Pulse Ring",
      sr: 1,
      ks: {
        o: {
          a: 1,
          k: [
            { t: 0, s: [100], e: [0] },
            { t: 60, s: [0] }
          ]
        },
        r: { a: 0, k: 0 },
        p: { a: 0, k: [30, 30, 0] },
        a: { a: 0, k: [0, 0, 0] },
        s: {
          a: 1,
          k: [
            { t: 0, s: [20, 20, 100], e: [100, 100, 100] },
            { t: 60, s: [100, 100, 100] }
          ]
        }
      },
      ao: 0,
      shapes: [
        {
          ty: "el",
          d: 1,
          s: { a: 0, k: [40, 40] },
          p: { a: 0, k: [0, 0] },
          nm: "Ellipse",
          mn: "ADBE Vector Shape - Ellipse"
        },
        {
          ty: "st",
          c: { a: 0, k: [0, 0.95, 1, 1] }, // Neon Cyan (#00f2fe)
          o: { a: 0, k: 100 },
          w: { a: 0, k: 3 },
          lc: 2,
          lj: 2,
          nm: "Stroke 1"
        }
      ]
    },
    {
      ddd: 0,
      ind: 2,
      ty: 4,
      nm: "Center Dot",
      sr: 1,
      ks: {
        o: { a: 0, k: 100 },
        r: { a: 0, k: 0 },
        p: { a: 0, k: [30, 30, 0] },
        a: { a: 0, k: [0, 0, 0] },
        s: {
          a: 1,
          k: [
            { t: 0, s: [80, 80, 100], e: [120, 120, 100] },
            { t: 30, s: [120, 120, 100], e: [80, 80, 100] },
            { t: 60, s: [80, 80, 100] }
          ]
        }
      },
      ao: 0,
      shapes: [
        {
          ty: "el",
          d: 1,
          s: { a: 0, k: [12, 12] },
          p: { a: 0, k: [0, 0] },
          nm: "Center Ellipse"
        },
        {
          ty: "fl",
          c: { a: 0, k: [0, 0.95, 1, 1] },
          o: { a: 0, k: 100 },
          nm: "Fill 1"
        }
      ]
    }
  ]
};

export const warningPulseLottie = {
  v: "5.7.4",
  fr: 30,
  ip: 0,
  op: 45,
  w: 60,
  h: 60,
  nm: "Warning Pulse",
  ddd: 0,
  assets: [],
  layers: [
    {
      ddd: 0,
      ind: 1,
      ty: 4,
      nm: "Alert Ring",
      sr: 1,
      ks: {
        o: {
          a: 1,
          k: [
            { t: 0, s: [90], e: [10] },
            { t: 45, s: [10] }
          ]
        },
        r: { a: 0, k: 0 },
        p: { a: 0, k: [30, 30, 0] },
        a: { a: 0, k: [0, 0, 0] },
        s: {
          a: 1,
          k: [
            { t: 0, s: [40, 40, 100], e: [110, 110, 100] },
            { t: 45, s: [110, 110, 100] }
          ]
        }
      },
      ao: 0,
      shapes: [
        {
          ty: "el",
          d: 1,
          s: { a: 0, k: [36, 36] },
          p: { a: 0, k: [0, 0] }
        },
        {
          ty: "st",
          c: { a: 0, k: [1, 0.09, 0.27, 1] }, // Crimson Red (#ff1744)
          o: { a: 0, k: 100 },
          w: { a: 0, k: 4 }
        }
      ]
    }
  ]
};
