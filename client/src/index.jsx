import React from 'react';
import ReactDOM from 'react-dom';
import { AppContainer } from 'react-hot-loader';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';
import { reducers, rootSaga } from 'reducers';
import createSagaMiddleware from 'redux-saga';
import App from 'app';

const sagaMiddleware = createSagaMiddleware();
const store = createStore(
  reducers,
  applyMiddleware(sagaMiddleware),
);
sagaMiddleware.run(rootSaga);

if (module.hot) {
  module.hot.accept('app', render);
  module.hot.accept('reducers', () => store.replaceReducer(reducers));
}

ReactDOM.render(
  <AppContainer>
    <Provider store={store}>
      <App />
    </Provider>
  </AppContainer>,
  document.getElementById('root'),
);
