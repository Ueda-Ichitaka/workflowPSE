import { Component, OnInit } from '@angular/core';
import { WorkflowService } from 'app/services/workflow.service';
import { Workflow } from 'app/models/Workflow';
import { Observable } from 'rxjs/Observable';
import { Router } from '@angular/router';
import { ProcessService } from 'app/services/process.service';
import { Process } from 'app/models/Process';
import { WpsService } from 'app/services/wps.service';
import { WPS } from '../../models/WPS';


// TODO: @Marcel add settings page
// - ressource for material design forms:
// https://material.angular.io/components/form-field/overview
@Component({
  selector: 'app-settings-page',
  templateUrl: './settings-page.component.html',
  styleUrls: ['./settings-page.component.scss']
})
export class SettingsPageComponent implements OnInit {

  wps_list: Observable<WPS[]>;

  update_options = [
    {value: "wps_provider0", displayed: "WPS Provider"},
    {value: "task1", displayed: "Task"}
  ];

  language_options = [
    {value: "deutsch0", displayed: "Deutsch"},
    {value: "english1", displayed: "English"}
  ];

  selected_language = "deutsch0";

  constructor(
    private processService: ProcessService,
    private wpsService: WpsService,
  ) {
    
  }

  public ngOnInit() {
    this.wps_list = this.wpsService.all();
  }

  public refresh() {
    // TODO signal server to refresh wps services
    console.log("services refreshed");
  }

  public onLangSelect(str) {
    this.selected_language = str;
  }

  public addWPS(url) {
    this.wpsService.create(url);
    
  }

  public remove(wps) {
    this.wpsService.remove(wps.id);
  }

}