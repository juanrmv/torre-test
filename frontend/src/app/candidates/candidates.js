class CandidatesController {
  /** @ngInject */
  constructor($http) {
    $http
      .get('http://localhost:8000/api/v1/candidates/')
      .then(response => {
        // eslint-disable-next-line angular/log
        console.log(response.data);
        this.candidates = response.data;
      });
  }
}

export const candidates = {
  template: require('./candidates.html'),
  controller: CandidatesController
};
