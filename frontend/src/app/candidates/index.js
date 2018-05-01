import angular from 'angular';

import {candidate} from './candidate';
import {candidates} from './candidates';

export const candidatesModule = 'candidates';

angular
  .module(candidatesModule, [])
  .component('torreCandidate', candidate)
  .component('torreCandidates', candidates);
