import {
  MatIconModule, MatInputModule, MatButtonModule, MatCheckboxModule, MatToolbarModule, MatTabsModule,
  MatFormFieldModule, MatCardModule, MatListModule, MatTooltipModule, MatChipsModule, MatDialogModule,
  MatExpansionModule, MatOptionModule, MatSelectModule, MatSidenavModule, MatMenuModule, MatSnackBarModule
} from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';
import { FlexLayoutModule } from '@angular/flex-layout';
import { NgModule } from '@angular/core';
import { EditorPageComponent } from 'app/pages/editor-page/editor-page.component';
import { WorkflowsPageComponent } from 'app/pages/workflows-page/workflows-page.component';
import { AppComponent } from 'app/components/app/app.component';
import { ProcessListComponent } from 'app/components/process-list/process-list.component';
import { ProcessDialogComponent } from 'app/components/process-dialog/process-dialog.component';
import { TaskComponent } from 'app/components/task/task.component';
import { EditorComponent } from 'app/components/editor/editor.component';
import { ProcessComponent } from 'app/components/process/process.component';
import { HttpClientModule } from '@angular/common/http';
import { ProcessService } from 'app/services/process.service';
import { WorkflowService } from 'app/services/workflow.service';
import { WpsService } from 'app/services/wps.service';
import { SettingsPageComponent } from 'app/pages/settings-page/settings-page.component';
import { ArtefactDialogComponent } from 'app/components/artefact-dialog/artefact-dialog.component';



const routes = [
  { path: '', component: EditorPageComponent },
  { path: 'editor', component: EditorPageComponent },
  { path: 'editor/:id', component: EditorPageComponent },
  { path: 'workflows', component: WorkflowsPageComponent },
  { path: 'settings', component: SettingsPageComponent },
];

@NgModule({
  declarations: [
    AppComponent,
    EditorPageComponent,
    WorkflowsPageComponent,
    SettingsPageComponent,
    ProcessListComponent,
    ProcessComponent,
    ProcessDialogComponent,
    ArtefactDialogComponent,
    EditorComponent,
    TaskComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    RouterModule.forRoot(routes),
    HttpClientModule,
    FlexLayoutModule,
    MatButtonModule,
    MatCheckboxModule,
    MatToolbarModule,
    MatTabsModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatCardModule,
    MatListModule,
    MatTooltipModule,
    MatChipsModule,
    MatDialogModule,
    MatExpansionModule,
    MatOptionModule,
    MatSelectModule,
    MatMenuModule,
    MatSnackBarModule
  ],
  entryComponents: [
    ProcessDialogComponent,
    ArtefactDialogComponent
  ],
  providers: [ProcessService, WorkflowService, WpsService, WpsService],
  bootstrap: [AppComponent]
})
export class AppModule { }
