import Axios from 'axios';

export const STATUS_404 = 'STATUS_404';

export function puzzleFetcher(puzzleId, headers = {}) {
  const SERVER_URL =
    (process.env.NODE_ENV === 'production')
      ? process.env.SERVER_URL_PROD
      : process.env.SERVER_URL_DEV;

  return Axios.get(`${SERVER_URL}/api/id/${puzzleId}`)
    .then((res) => {
      if (res.status === 200) {
        return res.json();
      } else if (res.status === 404) {
        return STATUS_404;
      }
      throw new Error('Invalid status', response.status);
    }).catch((err) => {
      console.error('Failed to fetch puzzle: ', puzzleId, err);
    });
}
