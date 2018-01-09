import {
  MatIconModule, MatInputModule, MatButtonModule, MatCheckboxModule, MatToolbarModule, MatTabsModule,
  MatFormFieldModule, MatCardModule, MatListModule, MatTooltipModule, MatChipsModule, MatDialogModule
} from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';
import { FlexLayoutModule } from '@angular/flex-layout';
import { NgModule } from '@angular/core';


import { AppComponent } from './app.component';
import { EditorPageComponent } from './editor-page/editor-page.component';
import { WorkflowsPageComponent } from './workflows-page/workflows-page.component';
import { ProcessListComponent } from './process-list/process-list.component';
import { ProcessComponent } from './process/process.component';
import { ProcessDetailDialogComponent } from './process-detail-dialog/process-detail-dialog.component';
import { HttpClientModule } from '@angular/common/http';
import { ProcessService } from 'app/services/process.service';
import { EditorComponent } from './editor/editor.component';
import { WorkflowProcessComponent } from './workflow-process/workflow-process.component';


const routes = [
  { path: '', component: EditorPageComponent },
  { path: 'editor', component: EditorPageComponent },
  { path: 'workflows', component: WorkflowsPageComponent },
];

@NgModule({
  declarations: [
    AppComponent,
    EditorPageComponent,
    WorkflowsPageComponent,
    ProcessListComponent,
    ProcessComponent,
    ProcessDetailDialogComponent,
    EditorComponent,
    WorkflowProcessComponent
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
  ],
  entryComponents: [
    ProcessDetailDialogComponent
  ],
  providers: [ProcessService],
  bootstrap: [AppComponent]
})
export class AppModule { }
