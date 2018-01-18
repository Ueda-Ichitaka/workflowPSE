import { Component, OnInit } from '@angular/core';
import { WorkflowService } from 'app/services/workflow.service';
import { Workflow } from 'app/models/Workflow';
import { Observable } from 'rxjs/Observable';
import { Router } from '@angular/router';
import { ProcessService } from 'app/services/process.service';
import { Process } from 'app/models/Process';
import { WpsService } from 'app/services/wps.service';


// TODO: @Marcel add settings page
// - ressource for material design forms:
// https://material.angular.io/components/form-field/overview
@Component({
  selector: 'app-settings-page',
  templateUrl: './settings-page.component.html',
  styleUrls: ['./settings-page.component.scss']
})
export class SettingsPageComponent implements OnInit {
  constructor(
    private processService: ProcessService,
    private wpsService: WpsService,
  ) {

  }

  public ngOnInit() {
  }

  public refresh() {
    console.log('services refreshed');
  }

}
